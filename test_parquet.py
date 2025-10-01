"""Simple test script to verify Parquet backend without Streamlit dependencies"""
import requests
import json
from io import BytesIO

def test_parquet_backend():
    """Test if the backend now returns actual Parquet format"""
    
    base_url = "https://ansebmrsurveysv1.oa.r.appspot.com"
    
    print("🔍 Testing new Parquet backend deployment...")
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        if response.status_code == 200:
            print("✅ Backend is online and healthy")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot reach backend: {e}")
        return
    
    # Test 2: Try Parquet endpoint
    try:
        print("\n🚀 Testing Parquet format endpoint...")
        
        parquet_url = f"{base_url}/api/responses"
        params = {
            "survey": "SB055_Profile_Survey1",
            "format": "parquet", 
            "limit": 10
        }
        
        response = requests.get(parquet_url, params=params, timeout=30)
        
        if response.status_code == 200:
            content = response.content
            print(f"📦 Received {len(content):,} bytes")
            
            # Check content type
            content_type = response.headers.get('content-type', '')
            print(f"📋 Content-Type: {content_type}")
            
            # Check if it's actual Parquet
            if content.startswith(b'PAR1') or (len(content) > 8 and content[-4:] == b'PAR1'):
                print("✅ SUCCESS! Backend is now returning actual Parquet format!")
                print(f"🎉 Parquet magic bytes detected in {len(content):,} byte response")
                
                # Try to parse it
                try:
                    import pandas as pd
                    df = pd.read_parquet(BytesIO(content))
                    print(f"✅ Successfully parsed Parquet: {len(df)} records, {len(df.columns)} columns")
                    print(f"📊 Sample columns: {list(df.columns)[:5]}")
                except ImportError:
                    print("⚠️  pandas/pyarrow not available for parsing test, but Parquet format confirmed!")
                except Exception as parse_error:
                    print(f"❌ Parquet parsing failed: {parse_error}")
                    
            elif content.startswith(b'{"') or content.startswith(b'[{'):
                print("⚠️  Backend still returning JSON format:")
                try:
                    json_preview = content[:200].decode('utf-8')
                    print(f"📄 JSON preview: {json_preview}...")
                except:
                    print("📄 JSON content detected but couldn't preview")
            else:
                print("❓ Unknown response format:")
                print(f"🔍 First 50 bytes: {content[:50]}")
                print(f"🔍 Last 50 bytes: {content[-50:]}")
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"📄 Response: {response.text[:200]}...")
            
    except requests.exceptions.Timeout:
        print("❌ Parquet request timed out (30s)")
    except Exception as e:
        print(f"❌ Parquet test failed: {e}")

if __name__ == "__main__":
    test_parquet_backend()