"""Message text for the engine's message keys, EN + AR. Placeholder until TASK_01_C's templates replace it.

Arabic is a first draft and has NOT been reviewed by a native speaker (AR_REVIEWED = False)."""

from rebound_engine.models import Language, UserProfile

AR_REVIEWED = False

MESSAGES: dict[str, dict[str, str]] = {
    "implementation_intention": {
        "en": "Let's make it smaller and tie it to something you already do: \"After ___, I will ___.\"",
        "ar": "لنجعلها أصغر ونربطها بشيء تفعله بالفعل: \"بعد ___، سأقوم بـ ___.\"",
    },
    "rest_is_ok": {
        "en": "Low energy is real. Today's step is lighter, and good sleep comes first.",
        "ar": "التعب أمر طبيعي. خطوة اليوم أخف، والنوم الجيد يأتي أولاً.",
    },
    "care": {
        "en": "Sorry you're unwell. Movement is paused; rest, and tell us when you feel OK again.",
        "ar": "نأسف لأنك لست بخير. أوقفنا خطوات الحركة؛ ارتح وأخبرنا عندما تشعر بتحسن.",
    },
    "new_time": {
        "en": "Your schedule changed, so we moved your step to a different time of day.",
        "ar": "تغيّر جدولك، لذلك نقلنا خطوتك إلى وقت آخر من اليوم.",
    },
    "indoor_swap": {
        "en": "We switched to an indoor version you can do at home.",
        "ar": "اخترنا لك نسخة داخلية يمكنك القيام بها في المنزل.",
    },
    "your_reason": {
        "en": "On tough days, remember why you started: \"{reason}\"",
        "ar": "في الأيام الصعبة، تذكّر لماذا بدأت: \"{reason}\"",
    },
    "your_reason_none": {
        "en": "Tough days happen. One small step still counts.",
        "ar": "الأيام الصعبة تحدث. خطوة صغيرة واحدة لا تزال مهمة.",
    },
    "thanks_for_sharing": {
        "en": "Thanks for telling us. We've adjusted tomorrow's plan.",
        "ar": "شكراً لإخبارنا. عدّلنا خطة الغد.",
    },
    "new_reminder": {
        "en": "Easy to forget. We'll remind you at a different time or in a different way.",
        "ar": "من السهل أن ننسى. سنذكّرك في وقت مختلف أو بطريقة مختلفة.",
    },
    "buddy_offer": {
        "en": "Want to do it with someone? Inviting a friend or family member often helps.",
        "ar": "هل تريد القيام بها مع شخص آخر؟ دعوة صديق أو أحد أفراد العائلة تساعد غالباً.",
    },
    "lighter_option": {
        "en": "Busy week ahead? Here's a lighter version.",
        "ar": "أسبوع مزدحم؟ إليك نسخة أخف.",
    },
    "check_with_doctor": {
        "en": "Please check with your doctor before increasing intensity.",
        "ar": "يرجى استشارة طبيبك قبل زيادة شدة النشاط.",
    },
    "see_doctor": {
        "en": "Based on your answers, please see a doctor before starting more activity. "
              "We'll start with sleep and gentle steps.",
        "ar": "بناءً على إجاباتك، يرجى مراجعة الطبيب قبل زيادة النشاط. سنبدأ بالنوم وخطوات لطيفة.",
    },
    # 998: UAE ambulance (confirmed on the u.ae official portal).
    # 800 SAKINA (800 725462): Abu Dhabi DoH 24/7 mental health support hotline, announced 3 Mar 2026:
    # https://www.doh.gov.ae/en/news/doh-activates-247-mental-health-support-hotline-800-sakina-(725462)
    "seek_care": {
        "en": "What you wrote sounds serious. We've paused coaching. Please contact a doctor now; "
              "in an emergency call 998 for an ambulance (UAE). If you're thinking of harming yourself, please "
              "talk to someone you trust or call the 24/7 mental health support line 800 SAKINA (800 725462).",
        "ar": "ما كتبته يبدو خطيراً. أوقفنا التدريب. يرجى التواصل مع طبيب الآن؛ وفي حالات الطوارئ اتصل بالرقم 998 "
              "للإسعاف (الإمارات). إذا كنت تفكر في إيذاء نفسك، تحدّث مع شخص تثق به أو اتصل بخط الدعم النفسي "
              "على مدار الساعة 800 SAKINA (800725462).",
    },
}

HOW_TO_TURN_OFF = {
    "en": "You can remove this goal or pause coaching any time in Settings. Nothing you've built is lost.",
    "ar": "يمكنك إزالة هذا الهدف أو إيقاف التدريب مؤقتاً في أي وقت من الإعدادات. لن تفقد أي تقدم.",
}


def render(key: str, profile: UserProfile) -> str:
    lang = "ar" if profile.basics.language == Language.ar else "en"
    if key == "your_reason":
        reason = profile.history.motivation_reason
        return MESSAGES[key][lang].format(reason=reason) if reason else MESSAGES["your_reason_none"][lang]
    return MESSAGES[key][lang]
