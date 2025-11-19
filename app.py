import streamlit as st
import streamlit.components.v1 as components
import qrcode
from io import BytesIO
import base64
from urllib.parse import quote

# 페이지 설정
st.set_page_config(
    page_title="📱 문자 보내기 📱",
    page_icon="📱",
    layout="centered"
)

# Base64 인코딩/디코딩 함수
def encode_base64(text):
    return base64.b64encode(text.encode('utf-8')).decode('utf-8')

def decode_base64(text):
    return base64.b64decode(text.encode('utf-8')).decode('utf-8')

# QR 코드 생성 함수
def generate_qr(url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf

# URL 파라미터 확인
query_params = st.query_params

# QR 접속 모드 (파라미터가 있을 때) - 원본 HTML과 동일한 구조
if 'p' in query_params and 'm' in query_params:
    phones_param = query_params['p']
    msg_param = query_params['m']
    
    phones = phones_param.split(',')
    decoded_msg = decode_base64(msg_param)
    
    # 원본 HTML을 그대로 사용 (JavaScript 포함)
    html_code = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>문자 보내기</title>
    <style>
    body {{
      background:#f4f4f4;
      font-family:"Malgun Gothic",sans-serif;
      margin:0;
      padding:20px;
    }}
    
    .mobile-all-btn {{
      background:#A8D5FE !important;
      color:#003B73 !important;
      font-weight:800 !important;
      border-radius:30px !important;
      padding:40px !important;
      width:100% !important;
      font-size:40px !important;
      border:none;
      cursor:pointer;
      margin-bottom:60px !important;
    }}
    
    .big-btn-mobile {{
      background:#C9B6E4 !important;
      color:white !important;
      font-weight:800 !important;
      border-radius:30px !important;
      padding:40px !important;
      width:100% !important;
      font-size:40px !important;
      border:none;
      cursor:pointer;
      margin-bottom:60px !important;
    }}
    </style>
    </head>
    <body>
    
    <div id="sendButtons"></div>
    
    <script>
    function decodeBase64(str) {{
      return decodeURIComponent(escape(atob(str)));
    }}
    
    // 모바일용 버튼 생성 (원본 HTML과 동일)
    function createSendButtons(phones, msg) {{
      const area = document.getElementById("sendButtons");
      area.innerHTML = "";
    
      // 전체 보내기
      const allBtn = document.createElement("button");
      allBtn.className = "mobile-all-btn";
      allBtn.innerHTML = `📢 전체에게 문자 보내기 (${{phones.length}}명)`;
    
      allBtn.onclick = () => {{
        const allNumbers = phones.join(",");
        const isiPhone = navigator.userAgent.toLowerCase().includes("iphone");
        let smsURL = "";
    
        if (isiPhone)
            smsURL = `sms:/open?addresses=${{allNumbers}}&body=${{encodeURIComponent(msg)}}`;
        else
            smsURL = `sms:${{allNumbers}}?body=${{encodeURIComponent(msg)}}`;
    
        window.location.href = smsURL;
        allBtn.style.display = "none";
      }};
      area.appendChild(allBtn);
    
      // 개별 버튼
      phones.forEach((p,i)=>{{
        const btn = document.createElement("button");
        btn.className = "big-btn-mobile";
        btn.innerHTML = `📨 [${{i+1}}] ${{p}}`;
    
        btn.onclick = () => {{
          const smsURL = `sms:${{p}}?body=${{encodeURIComponent(msg)}}`;
          window.location.href = smsURL;
          btn.style.display = "none";
        }};
        area.appendChild(btn);
      }});
    }}
    
    // 페이지 로드 시 실행
    const phones = decodeURIComponent("{phones_param}").split(",");
    const decodedMsg = decodeBase64(decodeURIComponent("{msg_param}"));
    createSendButtons(phones, decodedMsg);
    </script>
    
    </body>
    </html>
    """
    
    # HTML 전체를 렌더링
    components.html(html_code, height=2000, scrolling=True)

# 일반 모드 (QR 생성)
else:
    st.markdown('<h1 style="text-align:center;">📱 문자 보내기 📱</h1>', unsafe_allow_html=True)
    
    # 전화번호 입력
    st.markdown("### 핸드폰 번호")
    phone_input = st.text_area(
        "",
        placeholder="01012345678\n01098765432",
        height=120,
        key="phone_input",
        label_visibility="collapsed"
    )
    
    phones = [p.strip() for p in phone_input.split('\n') if p.strip()]
    if phones:
        st.info(f"입력된 번호: **{len(phones)}개**")
    
    # 문자 내용 입력
    st.markdown("### 문자 내용")
    msg_input = st.text_area(
        "",
        placeholder="여러 줄을 입력해도 됩니다.",
        height=120,
        key="msg_input",
        label_visibility="collapsed"
    )
    
    # QR 코드 생성 버튼
    if st.button("QR 코드 생성", type="primary", use_container_width=True):
        if not msg_input.strip():
            st.error("❌ 문자 내용을 입력하세요.")
        elif len(phones) == 0:
            st.error("❌ 번호를 입력하세요.")
        else:
            # URL 생성
            base64_msg = encode_base64(msg_input)
            p_param = quote(",".join(phones))
            m_param = quote(base64_msg)
            
            final_url = f"https://aisw000111.streamlit.app/?p={p_param}&m={m_param}"
            
            # QR 코드 생성
            st.markdown("---")
            st.markdown("### 🔲 QR 코드로 접속하세요")
            
            qr_img = generate_qr(final_url)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image(qr_img, use_container_width=True)
            
            st.success("✅ QR 코드가 생성되었습니다! 모바일에서 QR을 스캔하여 문자를 보내세요.")

    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; color:#999; font-size:14px;">
        💡 PC에서는 QR 코드를 생성하고, 모바일에서 스캔하여 문자를 보낼 수 있습니다.
    </div>
    """, unsafe_allow_html=True)
