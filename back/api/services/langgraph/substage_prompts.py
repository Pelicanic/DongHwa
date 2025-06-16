# 작성자: 최준혁
# 기능: 각 동화 단계(substage)에 맞는 [행동] 작성 지침 제공
# 마지막 수정일: 2025-06-16

def get_substage_instruction(substage: str) -> str:
    """세부 동화 단계에 따른 [행동] 작성 지침 반환"""
    if substage == "기1":
        return (
            "- [행동] should reflect the character’s daily routine or gentle habits.\n"
            "- Avoid mysterious or strange elements. Stay in peaceful, familiar territory.\n"
            "- Let the reader feel comfort and connection with the character's usual life.\n"
        )
    elif substage == "기2":
        return (
            "- A small strange or curious event appears.\n"
            "- [행동] should show curiosity, hesitation, or mild surprise.\n"
            "- Do not escalate tension too fast. Keep the tone gentle but intriguing.\n"
        )
    elif substage == "승1":
        return (
            "- First clear disruption or tension occurs.\n"
            "- [행동] should show the character noticing or beginning to engage with this problem.\n"
            "- Choices should reflect initial confusion, concern, or exploration.\n"
        )
    elif substage == "승2":
        return (
            "- Conflict expands: more involvement or discovery.\n"
            "- [행동] should reflect an attempt to solve something, or seek help or understanding.\n"
            "- It's okay to introduce a helper character if it fits the context.\n"
        )
    elif substage == "승3":
        return (
            "- Stakes rise. The character faces a clear obstacle or emotional conflict.\n"
            "- [행동] must reflect a meaningful reaction or attempted solution.\n"
            "- Choices can reflect courage, fear, or determination.\n"
        )
    elif substage == "전1":
        return (
            "- Crisis escalates: something may go wrong or feel overwhelming.\n"
            "- [행동] should focus on what the character does in the face of tension.\n"
            "- No new characters or settings. Stay focused.\n"
        )
    elif substage == "전2":
        return (
            "- Turning point or personal decision.\n"
            "- [행동] must reflect a key choice or inner realization.\n"
            "- Encourage self-reflection or bold internal resolution.\n"
        )
    elif substage == "결1":
        return (
            "- Things begin to resolve.\n"
            "- [행동] should reflect calming down, returning home, or solving the issue.\n"
            "- Use emotional softness and clear story progression.\n"
        )
    elif substage == "결2":
        return (
            "- Emotional closure.\n"
            "- [행동] should reflect peace, reflection, or a lesson learned.\n"
            "- Avoid any new drama or twists. Focus on serenity.\n"
        )
    elif substage == "에필로그":
        return (
            "- Only write a single sentence [문장] that peacefully ends the story.\n"
            "- No [질문] or [행동] should be provided.\n"
        )
    else:
        return ""
