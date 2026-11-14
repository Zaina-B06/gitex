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
    # Quit-smoking help: no phone number, because we couldn't verify one as current. Licensed clinics exist: Gulf News
    # reports 15 public and private clinics in the Emirate of Abu Dhabi licensed by ADPHC for smoking cessation:
    # https://gulfnews.com/living-in-uae/health/want-to-quit-smoking-heres-how-you-can-get-help-in-abu-dhabi-1.1685528737946
    "craving_tip": {
        "en": "Cravings usually pass in a few minutes. Today's step is a swap to ride it out. "
              "Want help quitting? Talk to your doctor, pharmacist or a licensed smoking-cessation clinic "
              "(ask your health centre).",
        "ar": "الرغبة في التدخين تزول غالباً خلال دقائق. خطوة اليوم بديل يساعدك على تجاوزها. "
              "هل تريد مساعدة للإقلاع؟ تحدّث مع طبيبك أو الصيدلي أو عيادة مرخّصة للإقلاع عن التدخين "
              "(اسأل مركزك الصحي).",
    },
    "stress_rest": {
        "en": "Stressful days happen. Today starts with a short rest step, and the rest is lighter.",
        "ar": "الأيام المجهدة تحدث. يبدأ اليوم بخطوة راحة قصيرة، وباقي الخطوات أخف.",
    },
    "smoke_free_space": {
        "en": "Being around smokers makes it harder. Today's step helps you take a break somewhere smoke-free.",
        "ar": "وجودك بين المدخنين يجعل الأمر أصعب. خطوة اليوم تساعدك على أخذ استراحة في مكان بلا تدخين.",
    },
    "pantry_swap": {
        "en": "No healthy food nearby? Today's step works with what you already have at home.",
        "ar": "لا يوجد طعام صحي قريب؟ خطوة اليوم تعتمد على ما لديك في المنزل.",
    },
    "diet_check_with_doctor": {
        "en": "Before changing what you eat, check with your doctor, especially with diabetes or in pregnancy.",
        "ar": "قبل تغيير طعامك، استشر طبيبك، خاصة مع السكري أو أثناء الحمل.",
    },
    "eid_rest": {
        "en": "Eid Mubarak! Enjoy the celebrations. Rest days don't count against you.",
        "ar": "عيد مبارك! استمتع بالاحتفال. أيام الراحة لا تُحسب ضدك.",
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
    # https://www.mediaoffice.abudhabi/en/health/department-of-health-abu-dhabi-activates-24-7-mental-health-support-hotline-800-sakina/
    "seek_care": {
        "en": "What you wrote sounds serious. We've paused coaching. Please contact a doctor now; "
              "in an emergency call 998 for an ambulance (UAE). If you're thinking of harming yourself, please "
              "talk to someone you trust or call the 24/7 mental health support line 800 SAKINA (800 725462).",
        "ar": "ما كتبته يبدو خطيراً. أوقفنا التدريب. يرجى التواصل مع طبيب الآن؛ وفي حالات الطوارئ اتصل بالرقم 998 "
              "للإسعاف (الإمارات). إذا كنت تفكر في إيذاء نفسك، تحدّث مع شخص تثق به أو اتصل بخط الدعم النفسي "
              "على مدار الساعة 800 SAKINA (800725462).",
    },
}

# Plan reasons (Task 05 Part A): plan choices only, never health outcomes; English <= 12 words.
REASONS: dict[str, dict[str, str]] = {
    "see_doctor_gentle": {
        "en": "Your health check suggests seeing a doctor, so we start gently.",
        "ar": "تشير إجاباتك الصحية إلى مراجعة الطبيب، لذلك نبدأ بلطف.",
    },
    "high_blood_pressure": {
        "en": "You mentioned high blood pressure, so movement stays at a moderate level.",
        "ar": "ذكرت ارتفاع ضغط الدم، لذلك تبقى الحركة بمستوى معتدل.",
    },
    "back_or_joint_pain": {
        "en": "You mentioned back or joint pain, so we chose low-impact movement.",
        "ar": "ذكرت ألماً في الظهر أو المفاصل، لذلك اخترنا حركة خفيفة على الجسم.",
    },
    "health_check": {
        "en": "Your health check answers keep movement at a moderate level.",
        "ar": "إجاباتك في الفحص الصحي تُبقي الحركة بمستوى معتدل.",
    },
    "pregnancy": {
        "en": "We picked pregnancy-safe steps for you.",
        "ar": "اخترنا لكِ خطوات آمنة أثناء الحمل.",
    },
    "mobility": {
        "en": "You told us about your mobility, so movement steps are seated.",
        "ar": "أخبرتنا عن حركتك، لذلك خطوات الحركة تكون جلوساً.",
    },
    "recovering": {
        "en": "You're recovering, so we start with the gentlest steps.",
        "ar": "أنت في فترة تعافٍ، لذلك نبدأ بأخف الخطوات.",
    },
    "recovery_first": {
        "en": "You're recovering or stressed, so rest steps come first.",
        "ar": "أنت في فترة تعافٍ أو ضغط، لذلك تأتي خطوات الراحة أولاً.",
    },
    "nutrition_first": {
        "en": "You mentioned diabetes, so meal steps come early.",
        "ar": "ذكرت السكري، لذلك تأتي خطوات الوجبات مبكراً.",
    },
    "rotating": {
        "en": "You chose many goals, so we take turns, three a day.",
        "ar": "اخترت أهدافاً كثيرة، لذلك نتناوب عليها، ثلاثة في اليوم.",
    },
    "senior_start": {
        "en": "We start with gentle, balance-friendly steps.",
        "ar": "نبدأ بخطوات لطيفة تساعد على التوازن.",
    },
    "small_start": {
        "en": "You're active on few days now, so we start small.",
        "ar": "أنت نشط في أيام قليلة حالياً، لذلك نبدأ بخطوات صغيرة.",
    },
    "fasting": {
        "en": "You fast in Ramadan, so steps then are fasting-friendly.",
        "ar": "أنت تصوم في رمضان، لذلك تكون الخطوات مناسبة للصيام.",
    },
}


def render_reason(key: str, profile: UserProfile) -> str:
    return REASONS[key]["ar" if profile.basics.language == Language.ar else "en"]


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
