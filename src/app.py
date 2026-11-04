import pandas as pd
import plotly.express as px
import streamlit as st
from src.llm import ask_openrouter

from src.metrics import (
    ticket_medio,
    receita_por_mes,
    total_pedidos,
    receita_total,
)

@st.cache_data
def load_data():
    return pd.read_csv("data_processed/sales_clean.csv", sep=";", decimal=",")

def main():
    st.set_page_config(
        page_title="DataPilot",
        page_icon=":material/analytics",
        layout="wide",
    )
    
    df = load_data()

    with st.sidebar:
        st.subheader(":material/tune: Controle")
        st.caption("Filtre a visualização")
        categories = st.pills(
            "Categorias",
            sorted(df["categoria"].unique()),
            selection_mode="multi",
            width="stretch",
            key="categories",
        )
    filtered_df = df[df["categoria"].isin(categories)] if categories else df 
    
    data = receita_por_mes(filtered_df)
    
    with st.container(horizontal=True,horizontal_alignment="distribute",vertical_alignment="center"):
        with st.container(gap="xxsmall"):
            st.title(":material/space_dashboard: :violet[DataPilot]", anchor=False)
            st.caption("Visão consolidada das vendas por categoria e período")
        st.badge("Painel de vendas", icon=":material/space_dashboard:", color='violet')
    st.space("small")
    
    revenue_panel, secondary_panel = st.columns([1.65,1])
    revenue_panel.metric(
        ":violet-badge[:material/paid: Receita total]",
        f"R$ {receita_total(filtered_df): ,.2f}",
        border=True,
        height=280,
        chart_data=data["receita"],
        chart_type="area",
        delta_color="violet",
    )
    with secondary_panel:
        st.metric(
            ":blue-badge[:material/receipt_long: Pedidos]",
            total_pedidos(filtered_df),
            border=True,
            height=132,
        )
        st.metric(
            ":green-badge[:material/analytics: Ticket médio]",
            f"R$ {ticket_medio(filtered_df):,.2f}",
            border=True,
            height=132,
        )
    st.space("small")
    fig = px.line(data, x="mes", y="receita", markers=True)
    fig.update_traces(
        line={"color": "#cba6f7", "width": 3},
        marker={"color": "#b4befe", "size": 7},
        fill="tozeroy",
        fillcolor="rgba(203, 166, 247, 0.08)",
    )
    fig.update_layout(
        height=380,
        margin={"l": 20, "r": 20, "t": 20, "b": 16},
        hovermode="x unified",
        xaxis_title=None,
        yaxis_title=None,
    )
    fig.update_yaxes(tickprefix="R$ ", tickformat="~s")

    with st.container(border=True):
        with st.container(
            horizontal=True,
            horizontal_alignment="distribute",
            vertical_alignment="center",
        ):
            st.subheader(":material/show_chart: Receita por mês")
            st.badge("Mensal", color="blue")

        st.plotly_chart(
            fig,
            width="stretch",
            config={"displayModeBar": False, "scrollZoom": False},
        )
def data_chat():
    st.markdown(
        """
        <style>
        [data-testid="stChatMessage"] p { font-size: 1.15rem; line-height: 1.7; }
        [data-testid="stChatInput"] textarea { font-size: 1.1rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.title(":material/forum: :violet[Converse com os dados]", anchor=False)
    st.caption("Pergunte sobre os indicadores calculados no painel.")

    messages = st.session_state.setdefault("data_chat_messages", [])
    for message in messages:
        with st.chat_message(message["role"], avatar=message.get("avatar")):
            st.write(message["content"])

    if question := st.chat_input(
        "Faça uma pergunta sobre os dados",
        submit_mode="disable",
    ):
        messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.write(question)
        with st.chat_message("assistant", avatar=":material/robot_2:"):
            with st.spinner("Consultando os dados..."):
                answer = ask_openrouter(question, load_data())
            st.write(answer)
        messages.append({"role": "assistant", "content": answer, "avatar": ":material/robot_2:"})
if __name__ == "__main__":
    main()