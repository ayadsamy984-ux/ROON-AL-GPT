import streamlit as st
import google.generativeai as genai
from web3 import Web3
import os

# 1. إعدادات الصفحة والذكاء الاصطناعي
st.set_page_config(page_title="ROON AL VIP", page_icon="💹", layout="wide")

# إعداد مفتاح API الخاص بك (ROON GPT)
genai.configure(api_key="AIzaSyDwMv7HS7fGQjA0IKIl0qEIQvCXt6W-G64")

# استخدام الموديل الذي أكد الترمينال أنه يعمل لديك
@st.cache_resource
def load_roon_model():
    return genai.GenerativeModel('models/gemini-3-flash-preview')

model = load_roon_model()

# --- البيانات الأساسية للمشروع ---
CONTRACT_ADDRESS = "0x881D12E3a4d32f3df439EF0F73546A9a67004723"
ADMIN_WALLET = "0x83b3864a8DdbF6F8eB666C66F11FA01d75eDE156"
BUY_URL = "https://thirdweb.com/binance/0x881D12E3a4d32f3df439EF0F73546A9a67004723"
MIN_TOKENS = 1000

# --- نظام الجلسة واللغة ---
if 'access_granted' not in st.session_state:
    st.session_state['access_granted'] = False
if 'lang' not in st.session_state:
    st.session_state['lang'] = "العربية"
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

with st.sidebar:
    st.session_state['lang'] = st.radio("Select Language", ["العربية", "English"])
    if st.button("مسح المحادثة / Clear"):
        st.session_state.chat_history = []
        st.rerun()

L = {
    "العربية": {
        "title": "ROON AL VIP",
        "access_text": "⚠️ تنبيه: المنصة حصرية لحاملي 1,000 قطعة أو أكثر من عملة $RAL",
        "wallet_input": "📍 أدخل عنوان محفظتك (Trust Wallet):",
        "btn_enter": "🚀 دخول المنصة",
        "btn_buy": "💳 شراء $RAL الآن",
        "err_bal": "⚠️ عذراً، رصيدك أقل من 1,000 قطعة.",
        "welcome": "✅ أهلاً بك في لوحة تحليلات ROON AL VIP",
        "chat_title": "🤖 ROON GPT (Gemini 3 Flash)",
        "dev_by": "تم التطوير بواسطة إياد سامي © 2026"
    },
    "English": {
        "title": "ROON AL VIP",
        "access_text": "⚠️ Exclusive for $RAL holders with 1,000+ tokens",
        "wallet_input": "📍 Enter your Trust Wallet address:",
        "btn_enter": "🚀 Enter Platform",
        "btn_buy": "💳 Buy $RAL Now",
        "err_bal": "⚠️ Minimum 1,000 tokens required.",
        "welcome": "✅ Welcome to ROON AL VIP Dashboard",
        "chat_title": "🤖 ROON GPT (Gemini 3 Flash)",
        "dev_by": "Developed by Ayad Sami © 2026"
    }
}
lang = st.session_state['lang']

# --- واجهة الدخول بالتحقق ---
if not st.session_state['access_granted']:
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        # عرض الشعار من ملف logo.jpg الموجود في مشروعك
        if os.path.exists("logo.jpg"):
            st.image("logo.jpg", use_container_width=True)
        else:
            st.markdown(f"<h1 style='text-align: center; color: gold;'>{L[lang]['title']}</h1>", unsafe_allow_html=True)
        
        st.info(L[lang]['access_text'])
        user_wallet = st.text_input(L[lang]['wallet_input'], placeholder="0x...")
        
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button(L[lang]['btn_enter'], use_container_width=True):
                # السماح بدخول أدمن المشروع أو الفحص عبر الشبكة
                if user_wallet.lower() == ADMIN_WALLET.lower():
                    st.session_state['access_granted'] = True
                    st.rerun()
                else:
                    try:
                        w3 = Web3(Web3.HTTPProvider('https://bsc-dataseed.binance.org/'))
                        abi = '[{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"type":"function"},{"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"}]'
                        contract = w3.eth.contract(address=w3.to_checksum_address(CONTRACT_ADDRESS), abi=abi)
                        raw_balance = contract.functions.balanceOf(w3.to_checksum_address(user_wallet)).call()
                        decimals = contract.functions.decimals().call()
                        balance = raw_balance / (10**decimals)
                        
                        if balance >= MIN_TOKENS:
                            st.session_state['access_granted'] = True
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(L[lang]['err_bal'])
                    except:
                        st.error("خطأ في الاتصال بالشبكة / تأكد من عنوان المحفظة")
        
        with btn_col2:
            st.link_button(L[lang]['btn_buy'], BUY_URL, use_container_width=True, type="primary")

# --- واجهة الشات (تظهر بعد الدخول فقط) ---
else:
    st.success(L[lang]['welcome'])
    st.header(L[lang]['chat_title'])

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("اسأل ROON GPT..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                # السياق الخاص بمشروع ROON AL
                response = model.generate_content(f"أنت المساعد الذكي لمشروع ROON AL. أجب باحترافية: {prompt}")
                st.markdown(response.text)
                st.session_state.chat_history.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"AI Error: {str(e)}")

st.markdown("---")
st.markdown(f"<p style='text-align: center;'>{L[lang]['dev_by']}</p>", unsafe_allow_html=True)
