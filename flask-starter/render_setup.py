import os
import base64

def decode_secret(env_var, output_filename):
    b64_string = os.environ.get(env_var)
    if not b64_string:
        print(f"Warning: {env_var} not found in environment. Skipping decoding for {output_filename}.")
        return

    try:
        # Pad with '=' if the length isn't a multiple of 4
        missing_padding = len(b64_string) % 4
        if missing_padding:
            b64_string += '=' * (4 - missing_padding)
            
        file_data = base64.b64decode(b64_string)
        with open(output_filename, 'wb') as f:
            f.write(file_data)
        print(f"Successfully decoded {env_var} to {output_filename}")
    except Exception as e:
        print(f"Error decoding {env_var}: {str(e)}")

if __name__ == "__main__":
    # Decode the Oracle Wallet zip
    decode_secret('WALLET_BASE64', 'Wallet_newsbrief.zip')
    
    # Extract the zip file so oracledb can read the config_dir
    import zipfile
    if os.path.exists('Wallet_newsbrief.zip'):
        with zipfile.ZipFile('Wallet_newsbrief.zip', 'r') as zip_ref:
            zip_ref.extractall('wallet')
        print("Extracted wallet to ./wallet directory")
    
    # Decode the OCI Private Key PEM
    decode_secret('OCI_KEY_BASE64', 'khuzaima.pem')
