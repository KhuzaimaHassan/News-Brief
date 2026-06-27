import os
import json
import oracledb
from dotenv import load_dotenv

load_dotenv()

pool = oracledb.create_pool(
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    dsn=os.getenv('DB_DSN'),
    config_dir=os.getenv('WALLET_LOCATION'),
    wallet_location=os.getenv('WALLET_LOCATION'),
    wallet_password=os.getenv('DB_PASSWORD'),
    min=1,
    max=4,
    increment=1
)

def setup_select_ai():
    with pool.acquire() as connection:
        with connection.cursor() as cursor:
            try:
                with open(os.getenv('OCI_KEY_FILE'), 'r') as f:
                    private_key = f.read()
            except Exception as e:
                print(f"Error reading private key file: {e}")
                return

            try:
                print("Dropping existing credential if it exists...")
                cursor.execute("""
                BEGIN
                    BEGIN
                        DBMS_CLOUD.DROP_CREDENTIAL(credential_name => 'OCI_GENAI_CRED');
                    EXCEPTION
                        WHEN OTHERS THEN NULL;
                    END;
                END;
                """)
                
                print("Creating OCI_GENAI_CRED credential...")
                cursor.execute("""
                BEGIN
                    DBMS_CLOUD.CREATE_CREDENTIAL(
                        credential_name => 'OCI_GENAI_CRED',
                        user_ocid       => :user_ocid,
                        tenancy_ocid    => :tenancy_ocid,
                        private_key     => :private_key,
                        fingerprint     => :fingerprint
                    );
                END;
                """, user_ocid=os.getenv('OCI_USER'), 
                     tenancy_ocid=os.getenv('OCI_TENANCY'), 
                     private_key=private_key, 
                     fingerprint=os.getenv('OCI_FINGERPRINT'))

                print("Dropping existing profile if it exists...")
                cursor.execute("""
                BEGIN
                    BEGIN
                        DBMS_CLOUD_AI.DROP_PROFILE(profile_name => 'VIBE_GENAI');
                    EXCEPTION
                        WHEN OTHERS THEN NULL;
                    END;
                END;
                """)

                print("Creating VIBE_GENAI profile...")
                attributes = json.dumps({
                    "provider": "oci",
                    "credential_name": "OCI_GENAI_CRED",
                    "model": "cohere.command-r-08-2024",
                    "oci_compartment_id": os.getenv('OCI_COMPARTMENT_ID')
                })
                
                cursor.execute("""
                BEGIN
                    DBMS_CLOUD_AI.CREATE_PROFILE(
                        profile_name => 'VIBE_GENAI',
                        attributes => :attributes
                    );
                END;
                """, attributes=attributes)

                cursor.execute("""
                BEGIN
                    DBMS_CLOUD_AI.SET_PROFILE(profile_name => 'VIBE_GENAI');
                END;
                """)
                print("Successfully created VIBE_GENAI Select AI profile!")
            except Exception as e:
                print(f"Error setting up Select AI: {e}")

if __name__ == "__main__":
    setup_select_ai()
