import streamlit as st
from answer import answer

st.title("Assistant ENSIAS")
st.caption("Réponses basées sur les documents officiels de l'ENSIAS")

question = st.chat_input("Pose ta question / Ask your question")

if question:
    with st.chat_message("user"):
        st.write(question)
    with st.chat_message("assistant"):
        with st.spinner("Recherche..."):
            text, hits = answer(question)
        st.write(text)
        if hits:
            with st.expander("Sources"):
                for i, h in enumerate(hits, 1):
                    m = h["meta"]
                    title = m["article"] or m["section"] or m["chapter"]
                    st.markdown(f"**[{i}] {title}**, page {m['page']} (score {h['score']:.2f})")
                    st.text(h["text"])