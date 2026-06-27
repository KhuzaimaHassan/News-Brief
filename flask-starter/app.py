from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import feedparser
from db import pool, memory
from oracleagentmemory.apis.searchscope import SearchScope

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/briefing")
def briefing_view():
    return render_template("briefing.html")

@app.route("/search_view")
def search_view():
    return render_template("search.html")

@app.route("/fetch", methods=["POST"])
def fetch():
    data = request.json
    feed_url = data.get("url")
    if not feed_url:
        return jsonify({"error": "No URL provided"}), 400
    
    import requests
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    try:
        response = requests.get(feed_url, headers=headers, timeout=10)
        feed = feedparser.parse(response.content)
    except Exception as e:
        return jsonify({"error": f"Failed to fetch feed: {str(e)}"}), 500
        
    items = []
    for entry in feed.entries[:20]:
        items.append({
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "summary": entry.get("summary", "")
        })
    return jsonify({"items": items})

@app.route("/summarise", methods=["POST"])
def summarise():
    data = request.json
    title = data.get("title", "")
    link = data.get("link", "")
    content = data.get("content", data.get("summary", ""))
    
    prompt = f"Summarise this article in two short sections. WHAT HAPPENED: one sentence. WHY IT MATTERS: one sentence. Title: {title}. Link: {link}\nContent: {content}"
    
    with pool.acquire() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
            SELECT DBMS_CLOUD_AI.GENERATE(
              prompt => :prompt, profile_name => 'VIBE_GENAI', action => 'chat'
            ) AS response FROM dual
            """, prompt=prompt)
            row = cursor.fetchone()
            if row:
                response_clob = row[0]
                summary_text = response_clob.read() if hasattr(response_clob, "read") else str(response_clob)
                return jsonify({"summary": summary_text})
    
    return jsonify({"error": "Failed to generate summary"}), 500

@app.route("/save", methods=["POST"])
def save():
    data = request.json
    headline = data.get("headline", "")
    summary = data.get("summary", "")
    story_text = f"{headline}\n{summary}"
    
    # 1. Search for highly similar prior stories to link as follow-up
    results = memory.search(query=story_text, scope=SearchScope(user_id="casius"))
    follow_up = None
    if results and len(results) > 0:
        top_result = results[0]
        # if similarity is high (e.g., > 0.8), consider it a follow-up
        score = getattr(top_result, 'similarity_score', getattr(top_result, 'distance', getattr(top_result, 'score', 0)))
        if score > 0.8 and top_result.content != story_text:
            # simple heuristic: the first line is the headline
            follow_up = top_result.content.split("\n")[0]
            
    # 2. Add to memory
    thread = memory.create_thread(user_id="casius")
    thread.add_memory(story_text)
    
    response = {"status": "saved"}
    if follow_up:
        response["follow_up"] = follow_up
    return jsonify(response)

@app.route("/brief", methods=["GET"])
def brief():
    try:
        # We use memory.search instead of raw SQL to avoid table name guessing and ORA errors if empty
        results = memory.search(query="news", scope=SearchScope(user_id="casius"))
        stories = "\n\n".join([r.content for r in results[:20] if not r.content.startswith("[DAILY BRIEFING]") and not r.content.startswith("STYLE RULE")])
        
        # Pull the style rule (procedural)
        style_results = memory.search(query="STYLE RULE", scope=SearchScope(user_id="casius"))
        style_context = "\n".join([r.content for r in style_results if "STYLE RULE" in r.content][:1])
        
    except Exception as e:
        print(f"Error fetching memories: {e}")
        stories = ""
        style_context = ""

    with pool.acquire() as connection:
        with connection.cursor() as cursor:
            if not stories:
                return jsonify({"briefing": "No stories found to brief."})

            import datetime
            today_date = datetime.datetime.now().strftime("%d %B %Y")
            
            prompt = f"""Here are today's stories:
{stories}

Here is your required stylistic format from memory:
{style_context}

Please generate the daily briefing. 
CRITICAL RULES:
1. Output ONLY the briefing text. Do NOT output any preamble like 'Here is your daily briefing:'.
2. You MUST use the exact Markdown formatting below. Do not use uppercase bullet points like "- WHAT HAPPENED:". Use bold inline text like "**What happened:**".

REQUIRED MARKDOWN TEMPLATE:
# AI Briefing, {today_date}

**TOP LINE**
[One flowing paragraph weaving the stories together. End with "The theme today: *[theme]*"]

**1. [Headline]**
*[Source]*
**What happened:** [2-4 sentences]
**Why it matters:** [2-4 sentences]
**Your Angle:** [AI Developer Advocate angle for Oracle]
**Sources:**
- [Source], "[Headline]", ([link])

[Continue for exactly 5 stories]
"""
            
            cursor.execute("""
            SELECT DBMS_CLOUD_AI.GENERATE(
              prompt => :prompt, profile_name => 'VIBE_GENAI', action => 'chat'
            ) AS response FROM dual
            """, prompt=prompt)
            row = cursor.fetchone()
            if row:
                import re
                response_clob = row[0]
                briefing_text = response_clob.read() if hasattr(response_clob, "read") else str(response_clob)
                
                # Strip chatty LLM preamble if it sneaks through
                briefing_text = re.sub(r"^(?:Sure|Here is|Here's|Okay|Certainly)[^\n]*:\s*\n*", "", briefing_text.strip(), flags=re.IGNORECASE).strip()
                
                try:
                    # Save the generated briefing into OracleAgentMemory
                    thread = memory.create_thread(user_id="casius")
                    thread.add_memory("[DAILY BRIEFING]\\n" + briefing_text)
                except Exception as save_err:
                    print(f"Error auto-saving briefing: {save_err}")
                
                return jsonify({"briefing": briefing_text})
                
    return jsonify({"error": "Failed to generate briefing"}), 500

@app.route("/search", methods=["POST"])
def search():
    data = request.json
    query = data.get("query", "")
    
    results = memory.search(query=query, scope=SearchScope(user_id="casius"))
    
    formatted_results = []
    for r in results:
        formatted_results.append({
            "type": r.record.record_type,
            "content": r.content,
            "score": getattr(r, 'similarity_score', getattr(r, 'distance', getattr(r, 'score', 0)))
        })
        
    return jsonify({"results": formatted_results})

@app.route("/past_briefings", methods=["GET"])
def past_briefings():
    try:
        results = memory.search(query="[DAILY BRIEFING]", scope=SearchScope(user_id="casius"))
        briefings = [r.content.replace("[DAILY BRIEFING]\\n", "") for r in results if r.content.startswith("[DAILY BRIEFING]")]
        return jsonify({"briefings": briefings})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
