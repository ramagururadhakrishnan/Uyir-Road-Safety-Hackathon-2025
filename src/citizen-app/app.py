"""
UYIR Road Safety Hackathon 2025 - Citizen Report & NFT Reward System

Author: Ramaguru Radhakrishnan
Email:  r_ramaguru@cb.amrita.edu
Date:   February 2025
License: MIT License
Version: 1.0

Description:
This Flask application allows citizens to report road safety issues and 
receive NFTs as a reward for their contribution. The NFTs are minted on 
the Ethereum Sepolia Testnet and can be viewed on OpenSea.

"""

from flask import Flask, render_template, request, jsonify
import json
import os
from PIL import Image, ImageDraw, ImageFont
import random
import requests
from web3 import Web3
import hashlib
import base58

app = Flask(__name__)

# 📂 Directory to store uploaded images
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 📄 Report storage file
REPORTS_FILE = "reports.json"

# 🔵 NFT.Storage API Key (Used to upload metadata and images to IPFS)
NFT_STORAGE_API_KEY = "<<API>>"

# 🔗 Ethereum Configuration (Sepolia Testnet)
INFURA_URL = "https://sepolia.infura.io/v3/<<API>>"
w3 = Web3(Web3.HTTPProvider(INFURA_URL))

# 🔑 Wallet Private Key & Address
PRIVATE_KEY = "<<PRIVATE KEY>>"
account = w3.eth.account.from_key(PRIVATE_KEY)

# 🎭 NFT Contract Address
#0x7300d7ba32bfa4d1d8c7ee29e3f4eeb1cfa3f102
NFT_CONTRACT_ADDRESS = w3.to_checksum_address("0x7300d7ba32bfa4d1d8c7ee29e3f4eeb1cfa3f102")

# ✅ File Paths (Ensure these directories exist)
METADATA_DIR = "metadata/"
os.makedirs(METADATA_DIR, exist_ok=True)


def initialize_reports_file():
    """Ensure the reports.json file exists and contains valid JSON."""
    if not os.path.exists(REPORTS_FILE):
        with open(REPORTS_FILE, 'w') as f:
            json.dump([], f, indent=4)

# ✅ Initialize reports file on startup
initialize_reports_file()


@app.route('/')
def home():
    """Render the home page."""
    return render_template('index.html')


@app.route('/submit-report', methods=['POST'])
def submit_report():
    """Handles citizen report submission and NFT reward generation."""
    print("📌 New Citizen Report Received")
    
    try:
        # 📝 Get form data
        issue_type = request.form.get('issueType')
        location = request.form.get('location')
        description = request.form.get('description')

        print(f"📍 Issue Type: {issue_type}, Location: {location}, Description: {description}")

        # 📸 Handle photo upload & watermarking
        photo_filename = None
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo.filename:
                photo_filename = os.path.join(UPLOAD_FOLDER, photo.filename)
                photo.save(photo_filename)

                print(f"📸 Photo Saved: {photo_filename}")
                photo_filename = add_watermark(photo_filename, "Citizen Report")  # Watermarked image

        # 🔄 Load existing reports
        if os.path.exists(REPORTS_FILE):
            with open(REPORTS_FILE, 'r') as f:
                reports = json.load(f)
        else:
            reports = []

        # 📝 Save report data
        report_data = {
            "issueType": issue_type,
            "location": location,
            "description": description,
            "nft": "",
            "photo": photo_filename if photo_filename else None
        }
        reports.append(report_data)

        # 💾 Write updated reports back to file
        with open(REPORTS_FILE, 'w') as f:
            json.dump(reports, f, indent=4)
            
        # 🎖️ Reward NFT to the user
        nft_link = reward_nft(issue_type, location, description)

        return jsonify({"message": "Report submitted successfully!", "nft_url": nft_link})

    except Exception as e:
        print(f"❌ ERROR: {e}")  # Log error
        return jsonify({"error": str(e)}), 500  # Return error response
        

def upload_to_nft_storage(metadata_filename):
    """Uploads NFT metadata to NFT.Storage and returns IPFS URL."""
    
    # ✅ API Base URL
    NFT_STORAGE_API_BASE = "https://preserve.nft.storage/api/v1"

    # ✅ Step 2: Upload Metadata JSON to NFT.Storage
    url = f"{NFT_STORAGE_API_BASE}/collection/add_tokens"
    headers = {
        "Authorization": f"Bearer {NFT_STORAGE_API_KEY}"
    }
    
    try: 
        with open(metadata_filename, "rb") as f:
            file_data = f.read()
            sha256_hash = hashlib.sha256(file_data).digest()  # 32-byte hash

        # 🔹 Convert to IPFS multihash format
        prefix = b'\x12\x20'  # 0x12 = SHA-256, 0x20 = 32 bytes
        multihash = prefix + sha256_hash  # Concatenate prefix + hash
        ipfs_hash = base58.b58encode(multihash).decode("utf-8")  # Base58 encode

        return ipfs_hash  # ✅ Return IPFS-compatible hash
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None


def add_watermark(image_path, watermark_text):
    """
    Adds a visible watermark to the uploaded image.

    Args:
        image_path (str): Path to the uploaded image.
        watermark_text (str): Text to add as a watermark.

    Returns:
        str: Path of the updated watermarked image.
    """
    print("🖼️ Adding Watermark to Image")
    
    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)

    # 📏 Determine font size dynamically
    font_size = max(30, image.size[1] // 15)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    # 🎯 Position watermark at bottom-right
    text_width, text_height = draw.textbbox((0, 0), watermark_text, font=font)[2:]
    position = (image.size[0] - text_width - 30, image.size[1] - text_height - 30)

    # 🔳 Draw background rectangle for better visibility
    rect_position = (position[0] - 10, position[1] - 5, position[0] + text_width + 10, position[1] + text_height + 5)
    draw.rectangle(rect_position, fill=(0, 0, 0, 150))  # Semi-transparent black box

    # ✍️ Draw watermark text
    draw.text(position, watermark_text, fill=(255, 255, 255, 255), font=font)

    # 💾 Save updated image
    image.save(image_path, "JPEG", quality=95)

    return image_path


def reward_nft(issue_type, location, description):
    """
    Issues an NFT as a reward for a citizen report.

    Args:
        issue_type (str): Type of issue reported.
        location (str): Location of the issue.
        description (str): Additional details.

    Returns:
        str: OpenSea URL of the minted NFT.
    """
    print("🎖️ Initiating NFT Minting Process")
    
    # 📝 Load Smart Contract ABI
    with open("TrafficNFT.json") as f:
        nft_abi = json.load(f)
    contract = w3.eth.contract(address=NFT_CONTRACT_ADDRESS, abi=nft_abi)

    # ✅ Check wallet balance
    balance = w3.eth.get_balance(account.address)
    print(f"💰 Wallet Balance: {w3.from_wei(balance, 'ether')} ETH")

    # 📝 Create NFT metadata
    metadata = {
        "name": f"Road Issue - {issue_type}",
        "description": f"Location: {location}, Details: {description}"
    }

    print("🖼️ NFT Metadata:\n", json.dumps(metadata, indent=4))

    # 🔢 Fetch latest nonce
    nonce = w3.eth.get_transaction_count(account.address)
    print(f"🔢 Transaction Nonce: {nonce}")

    # ⚡ Gas Fees (EIP-1559)
    maxPriorityFeePerGas = w3.to_wei('2', 'gwei')
    maxFeePerGas = w3.to_wei('50', 'gwei')
    
    print("🖼️ Uploading Metadata to IPFS...")
    
    # ✅ Save metadata locally before uploading
    metadata_filename = f"{METADATA_DIR}{issue_type.replace(' ', '_')}_{location.replace(' ', '_')}.json"
    with open(metadata_filename, "w") as f:
        json.dump(metadata, f, indent=4)

    print(f"📄 Metadata JSON saved: {metadata_filename}")
    
    # Upload to NFT.Storage
    try:
        ipfs_url = upload_to_nft_storage(metadata_filename)  # ✅ NFT.Storage (alternative)
        print(f"✅ IPFS URL: {ipfs_url}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None

    # 🛠️ Build the mint transaction
    txn = contract.functions.mintNFT(account.address, ipfs_url).build_transaction({
        'from': account.address,
        'gas': 3000000,
        'maxPriorityFeePerGas': maxPriorityFeePerGas,
        'maxFeePerGas': maxFeePerGas,
        'nonce': nonce
    })

    print("🛠️ Transaction Built:", json.dumps(txn, indent=4, default=str))

    # 🔑 Sign & Send Transaction
    signed_txn = w3.eth.account.sign_transaction(txn, private_key=PRIVATE_KEY)
    print("✅ Transaction Signed Successfully")
    
    # 🔹 Send Transaction
    try:
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        tx_hash_hex = tx_hash.hex()  # Convert HexBytes to string
        print(f"🚀 Sent Transaction: {tx_hash_hex}")

        # 🔹 Wait for Transaction Confirmation
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
        print(f"✅ Transaction Confirmed: {tx_receipt}")

        # 🔹 Generate OpenSea NFT URL
        nft_url = f"https://testnets.opensea.io/assets/sepolia/{NFT_CONTRACT_ADDRESS}/{nonce}"
        print(f"🎉 NFT Minted Successfully: {nft_url}")

        return nft_url  # Return OpenSea link

    except Exception as e:
        print(f"⚠️ Transaction Error: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
