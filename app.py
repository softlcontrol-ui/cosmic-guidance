        # チャット履歴を表示（スクロール可能）
        st.markdown("---")
        st.markdown("### 💬 会話履歴")
        
        # スクロール可能なコンテナ内に会話を表示
        chat_container = st.container(height=500)
        
        with chat_container:
            if st.session_state.messages:
                for message in st.session_state.messages:
                    role = message["role"]
                    content = message["content"]
                    
                    # ロールに応じたアイコンと背景色
                    if role == "assistant":
                        icon = "🤖"
                        bg_color = "rgba(74, 144, 226, 0.1)"
                        border_color = "#4a90e2"
                    else:
                        icon = "👤"
                        bg_color = "rgba(100, 100, 100, 0.1)"
                        border_color = "#666666"
                    
                    # メッセージを表示
                    st.markdown(f"""
                    <div style="
                        margin: 1rem 0;
                        padding: 1rem;
                        border-left: 3px solid {border_color};
                        background: {bg_color};
                        border-radius: 5px;
                    ">
                        <div style="font-weight: 600; margin-bottom: 0.5rem; color: {border_color};">
                            {icon} {'アトリ' if role == 'assistant' else 'あなた'}
                        </div>
                        <div style="white-space: pre-wrap; line-height: 1.6;">
                            {content}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("まだ会話がありません。クエストを受注して始めましょう！")
        
        # ユーザー入力を無効化（クエスト必須）
        if st.session_state.active_quest:
            st.info("💡 クエスト進行中です。行動完了後に報告してください。")
        else:
            st.info("💡 質問するには、上の「💬 相談する」または「🎯 月の課題」ボタンからクエストを受注してください。")
