import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from pypdf import PdfReader 
import time

from query_data import query_rag


def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text
  

def get_response(user_query: str, option: int = 0) -> str:
    return query_rag(user_query, option)


def stream_wrapper(text: str):
    for c in text:
        yield c + ""
        time.sleep(0.01)



def main():
    st.set_page_config(
        page_title="糖尿病问诊系统",
        page_icon=":stethoscope:",
    )
    st.header("糖尿病问诊智能小助手 :stethoscope:")

    # session_state.
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            AIMessage(content="您好，很高兴为您服务！您可以在下方输入您的问题，或从左侧区域上传您的文件，如诊断报告等。"),
        ]

    # conversation
    for message in st.session_state.chat_history:
        if isinstance(message, AIMessage):
            with st.chat_message("ai"):
                st.write(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message("user"):
                st.write(message.content)
    
    radio_container = st.empty()
    with radio_container:
        option = st.radio("选择报告详细程度：", ("简明", "标准", "详细"), horizontal=True, label_visibility="collapsed",)

    print(f"{option = }")

    trans_dict = {
        "简明": 0,
        "标准": 1,
        "详细": 2,
    }

    option = trans_dict[option]
    print(f"{option = }")

    # 添加自定义CSS
    st.markdown(
        """
        <style>
        .stRadio {
            position: fixed;
            bottom: 0;
            width: 100%;
            background: auto;
            padding: 0px 0;
            border-top: 0px solid #e6e6e6;
            z-index: 1000;
        }
        .stRadio div {
            margin-bottom: 10px;  /* 设置选项之间的间隔 */
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # JavaScript to scroll to the bottom of the page to see the radio buttons
    st.markdown(
        """
        <script>
        document.addEventListener('DOMContentLoaded', function() {
            window.scrollTo(0, document.body.scrollHeight);
        });
        </script>
        """,
        unsafe_allow_html=True
    )

    user_query = st.chat_input("请输入...")
    if user_query is not None and user_query.strip() != "":
        st.session_state.chat_history.append(HumanMessage(content=user_query))

        with st.chat_message("user"):
            st.markdown(user_query)

        with st.chat_message("ai"):
            with st.spinner("思考中……"):
                # response = st.write_stream(get_response(user_query, st.session_state.chat_history))
                response = get_response(user_query, option)
                # st.markdown(response)
                st.write_stream(stream_wrapper(response))

        st.session_state.chat_history.append(AIMessage(content=response))
    
    text = None
    with st.sidebar:
        st.subheader("此处上传文件")

        pdf_docs = st.file_uploader(
            label="请拖拽文件至此处，或在您的电脑里浏览您的文件并点击“确认”按钮。",
            accept_multiple_files=True,
            # type=["pdf", "txt"],
            # help="仅支持PDF文件，请勿上传其他格式。",
        )
        if st.button("确认"):
            with st.spinner("处理中……"):
                text = get_pdf_text(pdf_docs)

    if text is not None:
        with st.chat_message("ai"):
            with st.spinner("思考中……"):
                res = get_response(text, option)
                # st.markdown(res)
                st.write_stream(stream_wrapper(res))
        st.session_state.chat_history.append(AIMessage(content=res))



if __name__ == "__main__":
    main()