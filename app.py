import streamlit as st
import qrcode
from io import BytesIO
import base64
from urllib.parse import quote

st.set_page_config(page_title="디버그 모드", layout="centered")

# URL 파라미터 확인
query_params = st.query_params

st.title("🔍 디버그 모드")

# 파라미터 확인
st.markdown("### 📋 URL 파라미터 확인")
st.write("전체 파라미터:", dict(query_params))

if 'p' in query_params:
    st.success(f"✅ 'p' 파라미터 존재: {query_params['p'][:50]}...")
else:
    st.error("❌ 'p' 파라미터 없음")

if 'm' in query_params:
    st.success(f"✅ 'm' 파라미터 존재: {query_params['m'][:50]}...")
else:
    st.error("❌ 'm' 파라미터 없음")

# QR 모드인 경우
if 'p' in query_params and 'm' in query_params:
    st.markdown("---")
    st.markdown("### 🎯 파라미터 디코딩 테스트")
    
    try:
        phones_param = query_params['p']
        msg_param = query_params['m']
        
        st.write("**전화번호 (원본):**", phones_param)
        phones = phones_param.split(',')
        st.write("**전화번호 (분리):**", phones)
        
        st.write("**메시지 (Base64):**", msg_param[:100])
        decoded_msg = base64.b64decode(msg_param.encode('utf-8')).decode('utf-8')
        st.write("**메시지 (디코딩):**", decoded_msg)
        
        st.markdown("---")
        st.markdown("### 🔗 생성된 SMS URL")
        
        # Android URL
        android_url = f"sms:{','.join(phones)}?body={quote(decoded_msg)}"
        st.code(android_url, language=None)
        
        # iOS URL
        ios_url = f"sms:/open?addresses={','.join(phones)}&body={quote(decoded_msg)}"
        st.code(ios_url, language=None)
        
        st.markdown("---")
        st.markdown("### 🧪 테스트 버튼")
        st.markdown(f'<a href="{android_url}" style="display:block; background:#C9B6E4; color:white; padding:20px; text-align:center; text-decoration:none; border-radius:10px; margin:10px 0;">📱 Android 테스트</a>', unsafe_allow_html=True)
        st.markdown(f'<a href="{ios_url}" style="display:block; background:#A8D5FE; color:#003B73; padding:20px; text-align:center; text-decoration:none; border-radius:10px; margin:10px 0;">📱 iOS 테스트</a>', unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"❌ 에러 발생: {str(e)}")
        st.code(str(e))

else:
    st.markdown("---")
    st.info("💡 QR 코드를 스캔하면 이 화면에서 디버그 정보를 볼 수 있습니다.")
