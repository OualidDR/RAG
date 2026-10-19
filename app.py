import streamlit as st 
from rag import build_pipeline, retrieve, generate_answer

st.title("RAG")

@st.cache_resource

def load_pipeline():
    return build_pipeline("docs")

index, chunks = load_pipeline()

question = st.text_input("Ask a question about your documents !")

if question :
    results = retrieve(question, index, chunks, k = 2 )
    answer = generate_answer(question, results)
    st.write(answer)
    with st.expander("retrieved chunks") :
        for r in results :
            st.write(f"score: {r['score']:.2f}")
            st.text(r["text"])
            













































