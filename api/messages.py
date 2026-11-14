"""Message text for the engine's message keys, EN + AR, each with a plain-language variant (Task 05 Part D).

Every entry has "en", "ar", "simple_en", "simple_ar". Arabic is a first draft and has NOT been reviewed by a native
speaker (AR_REVIEWED = False); `python -m api.review_arabic` writes a review sheet for whoever checks it."""

from typing import Any

from rebound_engine.actions import load_actions
from rebound_engine.models import Language, ReadingLevel, UserProfile
from rebound_engine.recipes import load_recipes

AR_REVIEWED = False
TRANSLATION_NOTE = {
    "en": "Draft translation, pending native review.",
    "ar": "ترجمة أولية، بانتظار مراجعة متحدث أصلي.",
}

MESSAGES: dict[str, dict[str, str]] = {
    "implementation_intention": {
        "en": "Let's make it smaller and tie it to something you already do: \"After ___, I will ___.\"",
        "ar": "لنجعلها أصغر ونربطها بشيء تفعله بالفعل: \"بعد ___، سأقوم بـ ___.\"",
        "simple_en": "Make it small. Link it to something you already do: \"After ___, I will ___.\"",
        "simple_ar": "اجعلها صغيرة. اربطها بشيء تفعله كل يوم: \"بعد ___، سأقوم بـ ___.\"",
    },
    "rest_is_ok": {
        "en": "Low energy is real. Today's step is lighter, and good sleep comes first.",
        "ar": "التعب أمر طبيعي. خطوة اليوم أخف، والنوم الجيد يأتي أولاً.",
        "simple_en": "Being tired is OK. Today's step is easy. Sleep comes first.",
        "simple_ar": "التعب طبيعي. خطوة اليوم سهلة. النوم أولاً.",
    },
    "care": {
        "en": "Sorry you're unwell. Movement is paused; rest, and tell us when you feel OK again.",
        "ar": "نأسف لأنك لست بخير. أوقفنا خطوات الحركة؛ ارتح وأخبرنا عندما تشعر بتحسن.",
        "simple_en": "Sorry you are not well. We stopped your movement steps. Rest, and tell us when you feel better.",
        "simple_ar": "سلامتك. أوقفنا خطوات الحركة. ارتح، وأخبرنا عندما تتحسن.",
    },
    "new_time": {
        "en": "Your schedule changed, so we moved your step to a different time of day.",
        "ar": "تغيّر جدولك، لذلك نقلنا خطوتك إلى وقت آخر من اليوم.",
        "simple_en": "Your day changed. So we moved your step to a new time.",
        "simple_ar": "تغيّر يومك. نقلنا خطوتك إلى وقت جديد.",
    },
    "indoor_swap": {
        "en": "We switched to an indoor version you can do at home.",
        "ar": "اخترنا لك نسخة داخلية يمكنك القيام بها في المنزل.",
        "simple_en": "We gave you a step you can do at home.",
        "simple_ar": "اخترنا لك خطوة تقوم بها في البيت.",
    },
    "your_reason": {
        "en": "On tough days, remember why you started: \"{reason}\"",
        "ar": "في الأيام الصعبة، تذكّر لماذا بدأت: \"{reason}\"",
        "simple_en": "On hard days, think of why you started: \"{reason}\"",
        "simple_ar": "في الأيام الصعبة، تذكّر سببك: \"{reason}\"",
    },
    "your_reason_none": {
        "en": "Tough days happen. One small step still counts.",
        "ar": "الأيام الصعبة تحدث. خطوة صغيرة واحدة لا تزال مهمة.",
        "simple_en": "Hard days happen. One small step is still good.",
        "simple_ar": "الأيام الصعبة تمر. خطوة صغيرة تكفي.",
    },
    "thanks_for_sharing": {
        "en": "Thanks for telling us. We've adjusted tomorrow's plan.",
        "ar": "شكراً لإخبارنا. عدّلنا خطة الغد.",
        "simple_en": "Thank you for telling us. We changed your plan for tomorrow.",
        "simple_ar": "شكراً لك. غيّرنا خطة الغد.",
    },
    "new_reminder": {
        "en": "Easy to forget. We'll remind you at a different time or in a different way.",
        "ar": "من السهل أن ننسى. سنذكّرك في وقت مختلف أو بطريقة مختلفة.",
        "simple_en": "It is easy to forget. We will remind you at a new time or in a new way.",
        "simple_ar": "النسيان سهل. سنذكّرك في وقت آخر أو بطريقة أخرى.",
    },
    "buddy_offer": {
        "en": "Want to do it with someone? Inviting a friend or family member often helps.",
        "ar": "هل تريد القيام بها مع شخص آخر؟ دعوة صديق أو أحد أفراد العائلة تساعد غالباً.",
        "simple_en": "Do it with a friend or someone in your family. It often helps.",
        "simple_ar": "قم بها مع صديق أو أحد من أهلك. هذا يساعد.",
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
        "simple_en": "The wish to smoke goes away in a few minutes. Today's step helps you wait. "
                     "Want help to stop? Ask your doctor, a pharmacist or your health centre.",
        "simple_ar": "الرغبة في التدخين تزول بعد دقائق. خطوة اليوم تساعدك على الانتظار. "
                     "تريد مساعدة للإقلاع؟ اسأل طبيبك أو الصيدلي أو مركزك الصحي.",
    },
    "stress_rest": {
        "en": "Stressful days happen. Today starts with a short rest step, and the rest is lighter.",
        "ar": "الأيام المجهدة تحدث. يبدأ اليوم بخطوة راحة قصيرة، وباقي الخطوات أخف.",
        "simple_en": "Hard days happen. Today starts with a short rest. Your other steps are easier.",
        "simple_ar": "الأيام الصعبة تحدث. نبدأ اليوم براحة قصيرة. باقي خطواتك أسهل.",
    },
    "smoke_free_space": {
        "en": "Being around smokers makes it harder. Today's step helps you take a break somewhere smoke-free.",
        "ar": "وجودك بين المدخنين يجعل الأمر أصعب. خطوة اليوم تساعدك على أخذ استراحة في مكان بلا تدخين.",
        "simple_en": "It is harder near people who smoke. Today, take a break where no one smokes.",
        "simple_ar": "الأمر أصعب قرب المدخنين. اليوم، خذ استراحة في مكان بلا تدخين.",
    },
    "pantry_swap": {
        "en": "No healthy food nearby? Today's step works with what you already have at home.",
        "ar": "لا يوجد طعام صحي قريب؟ خطوة اليوم تعتمد على ما لديك في المنزل.",
        "simple_en": "No good food near you? Today's step uses food you have at home.",
        "simple_ar": "لا يوجد طعام صحي قربك؟ خطوة اليوم تستخدم ما في بيتك.",
    },
    "diet_check_with_doctor": {
        "en": "Before changing what you eat, check with your doctor, especially with diabetes or in pregnancy.",
        "ar": "قبل تغيير طعامك، استشر طبيبك، خاصة مع السكري أو أثناء الحمل.",
        "simple_en": "Before you change what you eat, ask your doctor. This matters most with diabetes or when "
                     "pregnant.",
        "simple_ar": "قبل أن تغيّر طعامك، اسأل طبيبك. هذا مهم مع السكري أو الحمل.",
    },
    "eid_rest": {
        "en": "Eid Mubarak! Enjoy the celebrations. Rest days don't count against you.",
        "ar": "عيد مبارك! استمتع بالاحتفال. أيام الراحة لا تُحسب ضدك.",
        "simple_en": "Eid Mubarak! Enjoy the day. It is fine to rest.",
        "simple_ar": "عيد مبارك! استمتع بيومك. لا بأس بالراحة.",
    },
    "lighter_option": {
        "en": "Busy week ahead? Here's a lighter version.",
        "ar": "أسبوع مزدحم؟ إليك نسخة أخف.",
        "simple_en": "Busy week? Here is an easier step.",
        "simple_ar": "أسبوع مزدحم؟ هذه خطوة أسهل.",
    },
    "check_with_doctor": {
        "en": "Please check with your doctor before increasing intensity.",
        "ar": "يرجى استشارة طبيبك قبل زيادة شدة النشاط.",
        "simple_en": "Please ask your doctor before you push yourself harder.",
        "simple_ar": "اسأل طبيبك قبل أن تقوم بتمارين أصعب.",
    },
    "see_doctor": {
        "en": "Based on your answers, please see a doctor before starting more activity. "
              "We'll start with sleep and gentle steps.",
        "ar": "بناءً على إجاباتك، يرجى مراجعة الطبيب قبل زيادة النشاط. سنبدأ بالنوم وخطوات لطيفة.",
        "simple_en": "Please see a doctor before you move more. We will start with sleep and easy steps.",
        "simple_ar": "راجع الطبيب قبل أن تزيد حركتك. سنبدأ بالنوم وخطوات سهلة.",
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
              "على مدار الساعة 800 SAKINA (800 725462).",
        "simple_en": "This sounds serious. We have stopped coaching. Please call a doctor now. "
                     "If it is an emergency, call 998 for an ambulance. If you think of hurting yourself, talk to "
                     "someone you trust. Or call 800 SAKINA (800 725462). It is open day and night.",
        "simple_ar": "ما كتبته يبدو خطيراً. أوقفنا التدريب. اتصل بطبيب الآن. في الطوارئ اتصل بالرقم 998 للإسعاف. "
                     "إذا فكّرت في إيذاء نفسك، تحدّث مع شخص تثق به. أو اتصل بالرقم 800 SAKINA (800 725462). "
                     "الخط يعمل ليلاً ونهاراً.",
    },
}

# Plan reasons (Task 05 Part A): plan choices only, never health outcomes; English <= 12 words.
REASONS: dict[str, dict[str, str]] = {
    "see_doctor_gentle": {
        "en": "Your health check suggests seeing a doctor, so we start gently.",
        "ar": "تشير إجاباتك الصحية إلى مراجعة الطبيب، لذلك نبدأ بلطف.",
        "simple_en": "Your answers say to see a doctor, so we start slowly.",
        "simple_ar": "إجاباتك تقول: راجع الطبيب. لذلك نبدأ ببطء.",
    },
    "high_blood_pressure": {
        "en": "You mentioned high blood pressure, so movement stays at a moderate level.",
        "ar": "ذكرت ارتفاع ضغط الدم، لذلك تبقى الحركة بمستوى معتدل.",
        "simple_en": "You told us about high blood pressure, so movement is not too hard.",
        "simple_ar": "أخبرتنا عن ضغط الدم المرتفع، لذلك لن تكون الحركة شديدة.",
    },
    "back_or_joint_pain": {
        "en": "You mentioned back or joint pain, so we chose low-impact movement.",
        "ar": "ذكرت ألماً في الظهر أو المفاصل، لذلك اخترنا حركة خفيفة على الجسم.",
        "simple_en": "You told us about back or joint pain, so we chose gentle movement.",
        "simple_ar": "أخبرتنا عن ألم الظهر أو المفاصل، لذلك اخترنا حركة لطيفة.",
    },
    "health_check": {
        "en": "Your health check answers keep movement at a moderate level.",
        "ar": "إجاباتك في الفحص الصحي تُبقي الحركة بمستوى معتدل.",
        "simple_en": "Because of your health answers, movement is not too hard.",
        "simple_ar": "بسبب إجاباتك الصحية، لن تكون الحركة شديدة.",
    },
    "pregnancy": {
        "en": "We picked pregnancy-safe steps for you.",
        "ar": "اخترنا لكِ خطوات آمنة أثناء الحمل.",
        "simple_en": "We chose steps that are safe when you are pregnant.",
        "simple_ar": "كل خطواتكِ آمنة في الحمل.",
    },
    "mobility": {
        "en": "You told us about your mobility, so movement steps are seated.",
        "ar": "أخبرتنا عن حركتك، لذلك خطوات الحركة تكون جلوساً.",
        "simple_en": "You told us how you move, so you can do the steps sitting down.",
        "simple_ar": "أخبرتنا عن حركتك، فتقوم بالخطوات وأنت جالس.",
    },
    "recovering": {
        "en": "You're recovering, so we start with the gentlest steps.",
        "ar": "أنت في فترة تعافٍ، لذلك نبدأ بأخف الخطوات.",
        "simple_en": "You are getting better, so we start with the easiest steps.",
        "simple_ar": "أنت تتعافى، لذلك نبدأ بأسهل الخطوات.",
    },
    "recovery_first": {
        "en": "You're recovering or stressed, so rest steps come first.",
        "ar": "أنت في فترة تعافٍ أو ضغط، لذلك تأتي خطوات الراحة أولاً.",
        "simple_en": "You are getting better or under stress, so rest comes first.",
        "simple_ar": "أنت تتعافى أو تحت ضغط، لذلك الراحة أولاً.",
    },
    "nutrition_first": {
        "en": "You mentioned diabetes, so meal steps come early.",
        "ar": "ذكرت السكري، لذلك تأتي خطوات الوجبات مبكراً.",
        "simple_en": "You told us about diabetes, so food steps come early.",
        "simple_ar": "أخبرتنا عن السكري، فنبدأ مبكراً بخطوات الطعام.",
    },
    "rotating": {
        "en": "You chose many goals, so we take turns, three a day.",
        "ar": "اخترت أهدافاً كثيرة، لذلك نتناوب عليها، ثلاثة في اليوم.",
        "simple_en": "You have many goals. We do three a day, in turns.",
        "simple_ar": "لديك أهداف كثيرة. نعمل على ثلاثة كل يوم بالتناوب.",
    },
    "senior_start": {
        "en": "We start with gentle, balance-friendly steps.",
        "ar": "نبدأ بخطوات لطيفة تساعد على التوازن.",
        "simple_en": "We start with easy steps that help your balance.",
        "simple_ar": "نبدأ بخطوات سهلة تقوّي توازنك.",
    },
    "small_start": {
        "en": "You're active on few days now, so we start small.",
        "ar": "أنت نشط في أيام قليلة حالياً، لذلك نبدأ بخطوات صغيرة.",
        "simple_en": "Right now you move on few days, so we start small.",
        "simple_ar": "أنت تتحرك أياماً قليلة الآن، فنبدأ بخطوات صغيرة.",
    },
    "fasting": {
        "en": "You fast in Ramadan, so steps then are fasting-friendly.",
        "ar": "أنت تصوم في رمضان، لذلك تكون الخطوات مناسبة للصيام.",
        "simple_en": "You fast in Ramadan, so your steps then are safe when fasting.",
        "simple_ar": "أنت تصوم رمضان، فخطواتك فيه تناسب الصيام.",
    },
}


ROTATION_NOTE = {
    "en": "You have more than 3 goals, so your third step changes each day.",
    "ar": "لديك أكثر من 3 أهداف، لذلك تتغير خطوتك الثالثة كل يوم.",
    "simple_en": "You have more than 3 goals. Your third step changes each day.",
    "simple_ar": "عندك أكثر من 3 أهداف. خطوتك الثالثة تتبدل كل يوم.",
}


# Encouragement moments (Task 05 Part C). Several per moment, rotated by day. Never a count, never streak language,
# never how many days were missed (tested).
ENCOURAGEMENT: dict[str, list[dict[str, str]]] = {
    "first_day_done": [
        {"en": "You did your first step. That's how every habit starts.",
         "ar": "أنجزت خطوتك الأولى. هكذا تبدأ كل عادة.",
         "simple_en": "Well done on your first step!", "simple_ar": "أحسنت في خطوتك الأولى!"},
        {"en": "First step done. Small steps add up.",
         "ar": "أنجزت الخطوة الأولى. الخطوات الصغيرة تتراكم.",
         "simple_en": "Your first step is done!", "simple_ar": "خطوتك الأولى تمت!"},
        {"en": "A great start. Tomorrow's step will be just as small.",
         "ar": "بداية رائعة. خطوة الغد ستكون صغيرة أيضاً.",
         "simple_en": "Great start!", "simple_ar": "بداية رائعة!"},
    ],
    "three_good_days": [
        {"en": "You keep showing up. That's how habits grow.",
         "ar": "أنت تواصل الحضور. هكذا تنمو العادات.",
         "simple_en": "You keep going. Well done!", "simple_ar": "تواصل التقدم. أحسنت!"},
        {"en": "A good few days. This is starting to feel like yours.",
         "ar": "أيام جيدة. بدأت هذه العادة تصبح عادتك.",
         "simple_en": "Good days. Keep going!", "simple_ar": "أيام جيدة. استمر!"},
        {"en": "Steady and kind to yourself. Nice work.",
         "ar": "ثابت ولطيف مع نفسك. عمل جميل.",
         "simple_en": "Nice work!", "simple_ar": "عمل جميل!"},
    ],
    "comeback": [
        {"en": "We missed you. Glad you're back.",
         "ar": "افتقدناك. سعداء بعودتك.",
         "simple_en": "Welcome back!", "simple_ar": "أهلاً بعودتك!"},
        {"en": "Welcome back. Picking it up again is the skill that matters.",
         "ar": "أهلاً بعودتك. العودة من جديد هي المهارة الأهم.",
         "simple_en": "Good to see you again!", "simple_ar": "سعداء برؤيتك مجدداً!"},
        {"en": "You're back. Every return makes the habit stronger.",
         "ar": "لقد عدت. كل عودة تجعل العادة أقوى.",
         "simple_en": "You came back. Well done!", "simple_ar": "لقد عدت. أحسنت!"},
    ],
    "habit_strength_50": [
        {"en": "This habit is halfway to feeling automatic.",
         "ar": "هذه العادة في منتصف الطريق لتصبح تلقائية.",
         "simple_en": "This habit is getting easier!", "simple_ar": "هذه العادة تصبح أسهل!"},
        {"en": "Your habit ring is half full. It's becoming part of your day.",
         "ar": "حلقة عادتك نصف ممتلئة. أصبحت جزءاً من يومك.",
         "simple_en": "Your habit is growing!", "simple_ar": "عادتك تكبر!"},
        {"en": "This one is really taking root.",
         "ar": "هذه العادة تترسخ فعلاً.",
         "simple_en": "This habit is growing strong!", "simple_ar": "هذه العادة تقوى!"},
    ],
    "first_week_done": [
        {"en": "Your first week with Rebound. Thank you for sticking with it.",
         "ar": "أسبوعك الأول مع Rebound. شكراً لاستمرارك.",
         "simple_en": "Your first week is done!", "simple_ar": "أسبوعك الأول تم!"},
        {"en": "A whole week of looking after yourself.",
         "ar": "أسبوع كامل من الاهتمام بنفسك.",
         "simple_en": "Your first week. Well done!", "simple_ar": "أسبوعك الأول. أحسنت!"},
        {"en": "First week done. You've made room for this in your life.",
         "ar": "انتهى الأسبوع الأول. لقد أفسحت لهذا مكاناً في حياتك.",
         "simple_en": "Great first week!", "simple_ar": "أسبوع أول رائع!"},
    ],
    "tried_something_new": [
        {"en": "You tried something new today. Nice.",
         "ar": "جربت شيئاً جديداً اليوم. رائع.",
         "simple_en": "You tried something new!", "simple_ar": "جربت شيئاً جديداً!"},
        {"en": "A new step, done. You're growing.",
         "ar": "خطوة جديدة أنجزتها. أنت تتقدم.",
         "simple_en": "New step done!", "simple_ar": "خطوة جديدة تمت!"},
        {"en": "Trying new things keeps a habit fresh. Well done.",
         "ar": "تجربة أشياء جديدة تبقي العادة متجددة. أحسنت.",
         "simple_en": "Well done trying something new!", "simple_ar": "أحسنت على تجربة شيء جديد!"},
    ],
}


HOW_TO_TURN_OFF = {
    "en": "You can remove this goal or pause coaching any time in Settings. Nothing you've built is lost.",
    "ar": "يمكنك إزالة هذا الهدف أو إيقاف التدريب مؤقتاً في أي وقت من الإعدادات. لن تفقد أي تقدم.",
    "simple_en": "You can stop this goal or take a break any time in Settings. You keep all you have done.",
    "simple_ar": "تقدر توقف هذا الهدف أو تأخذ استراحة في أي وقت من الإعدادات. لن تخسر ما أنجزته.",
}

# Onboarding text (AGENTS.md §4.3, §4.5, §4.7, §4.8). Health-check questions paraphrase PAR-Q+; not copied.
QUESTIONS: dict[str, dict[str, str]] = {
    "heart_condition_or_high_bp": {
        "en": "Has a doctor ever said you have a heart condition or high blood pressure?",
        "ar": "هل قال لك طبيب إن لديك مشكلة في القلب أو ارتفاعاً في ضغط الدم؟",
        "simple_en": "Do you have a heart problem or high blood pressure?",
        "simple_ar": "هل عندك مشكلة في القلب أو ضغط دم مرتفع؟",
    },
    "chest_pain": {
        "en": "Do you feel pain in your chest at rest, during daily activities, or when you exercise?",
        "ar": "هل تشعر بألم في صدرك أثناء الراحة أو الأنشطة اليومية أو عند ممارسة الرياضة؟",
        "simple_en": "Do you get pain in your chest, at rest or when you move?",
        "simple_ar": "هل تشعر بألم في الصدر، وأنت مرتاح أو وأنت تتحرك؟",
    },
    "dizziness_or_fainting": {
        "en": "In the last 12 months, have you lost your balance because of dizziness, or fainted?",
        "ar": "خلال آخر 12 شهراً، هل فقدت توازنك بسبب الدوخة، أو أُغمي عليك؟",
        "simple_en": "In the last year, did you feel dizzy and lose your balance, or faint?",
        "simple_ar": "في السنة الماضية، هل دُخت وفقدت توازنك، أو أُغمي عليك؟",
    },
    "other_long_term_condition": {
        "en": "Do you have another long-term health condition, such as diabetes or asthma?",
        "ar": "هل لديك حالة صحية مزمنة أخرى، مثل السكري أو الربو؟",
        "simple_en": "Do you have another health problem that lasts a long time? For example, diabetes or asthma.",
        "simple_ar": "هل عندك مرض آخر يدوم طويلاً، مثل السكري أو الربو؟",
    },
    "prescribed_medication": {
        "en": "Do you take prescribed medicine for a long-term condition?",
        "ar": "هل تتناول دواءً موصوفاً لحالة صحية مزمنة؟",
        "simple_en": "Do you take medicine from a doctor for a health problem that lasts a long time?",
        "simple_ar": "هل تأخذ دواء من الطبيب لمرض يدوم طويلاً؟",
    },
    "bone_joint_muscle_problem": {
        "en": "Do you have a bone, joint or muscle problem that more activity could make worse?",
        "ar": "هل لديك مشكلة في العظام أو المفاصل أو العضلات قد تزداد سوءاً مع زيادة النشاط؟",
        "simple_en": "Do you have a bone, joint or muscle problem that more movement could make worse?",
        "simple_ar": "هل عندك مشكلة في العظام أو المفاصل أو العضلات تسوء مع الحركة؟",
    },
    "supervised_exercise_only": {
        "en": "Has a doctor said you should only exercise with medical supervision?",
        "ar": "هل قال لك طبيب أن تمارس الرياضة فقط تحت إشراف طبي؟",
        "simple_en": "Did a doctor say you should only exercise with a nurse or doctor there?",
        "simple_ar": "هل قال لك الطبيب ألا تتمرن إلا مع طبيب أو ممرض؟",
    },
    "pregnant": {
        "en": "Are you currently pregnant?",
        "ar": "هل أنتِ حامل حالياً؟",
        "simple_en": "Are you pregnant now?",
        "simple_ar": "هل أنتِ حامل الآن؟",
    },
    "mobility_limitation": {
        "en": "Do you have any difficulty moving around?",
        "ar": "هل لديك أي صعوبة في الحركة؟",
        "simple_en": "Is it hard for you to move around?",
        "simple_ar": "هل تجد الحركة صعبة؟",
    },
}

WHY_WE_ASK: dict[str, dict[str, str]] = {
    "screening": {
        "en": "We ask so that every step we suggest is safe for you.",
        "ar": "نسأل لكي تكون كل خطوة نقترحها آمنة لك.",
        "simple_en": "We ask so your steps are safe.",
        "simple_ar": "نسأل لتكون خطواتك آمنة.",
    },
    "body": {
        "en": "Used only to set a safe starting intensity, never shown as a target.",
        "ar": "تُستخدم فقط لتحديد شدة بداية آمنة، ولا تُعرض أبداً كهدف.",
        "simple_en": "We use this only to pick a safe start. We never show it as a goal.",
        "simple_ar": "نستخدمها فقط لبداية آمنة. لن نعرضها كهدف.",
    },
    "motivation_reason": {
        "en": "We'll remind you of this on tough days.",
        "ar": "سنذكّرك بهذا في الأيام الصعبة.",
        "simple_en": "We will show you this on hard days.",
        "simple_ar": "سنعرض لك هذا عندما يصعب يومك.",
    },
    "conditions": {
        "en": "So your plan fits what you're dealing with.",
        "ar": "لكي تناسب خطتك ما تمر به.",
        "simple_en": "So your plan fits your health.",
        "simple_ar": "لتناسب خطتك وضعك الصحي.",
    },
}

# Shown first on the Arabic review sheet: a wrong word here could hurt someone.
SAFETY_KEYS = frozenset({
    "message.seek_care", "message.see_doctor", "message.check_with_doctor", "message.care",
    "message.diet_check_with_doctor", "message.craving_tip", "reason.see_doctor_gentle",
    *(f"question.{q}" for q in QUESTIONS), "why.screening",
})


def _lang_key(lang: Language, level: ReadingLevel) -> str:
    code = "ar" if lang == Language.ar else "en"
    return f"simple_{code}" if level == ReadingLevel.simple else code


def pick(entry: dict[str, str], lang: Language, level: ReadingLevel = ReadingLevel.standard) -> str:
    return entry[_lang_key(lang, level)]


def _for(entry: dict[str, str], profile: UserProfile) -> str:
    return pick(entry, profile.basics.language, profile.preferences.reading_level)


def render_reason(key: str, profile: UserProfile) -> str:
    return _for(REASONS[key], profile)


def render_rotation_note(profile: UserProfile) -> str:
    return _for(ROTATION_NOTE, profile)


def render_encouragement(moment: str, profile: UserProfile, day: int) -> str:
    variants = ENCOURAGEMENT[moment]
    return _for(variants[day % len(variants)], profile)


def render(key: str, profile: UserProfile) -> str:
    if key == "your_reason":
        reason = profile.history.motivation_reason
        return _for(MESSAGES[key], profile).format(reason=reason) if reason else _for(MESSAGES["your_reason_none"],
                                                                                         profile)
    return _for(MESSAGES[key], profile)


def onboarding_text(lang: Language, level: ReadingLevel) -> dict[str, Any]:
    example = next(a for a in load_actions() if a.id == "mv_t1_balance")
    code = "ar" if lang == Language.ar else "en"
    return {
        "questions": {k: pick(v, lang, level) for k, v in QUESTIONS.items()},
        "why_we_ask": {k: pick(v, lang, level) for k, v in WHY_WE_ASK.items()},
        # One plain example of each level, so people can choose (Task 05 Part D).
        "reading_level_examples": {"standard": getattr(example.title, code), "simple": getattr(example.simple, code)},
        "translation_note": None if AR_REVIEWED or lang != Language.ar else TRANSLATION_NOTE[code],
    }


def catalogue() -> list[dict[str, Any]]:
    """Every user-facing string, one row per key with "en", "ar", "simple_en", "simple_ar" (None if a variant
    doesn't exist) and "safety". Used by the readability/safety tests and the Arabic review sheet."""
    rows: list[dict[str, Any]] = []

    def add(key: str, entry: dict[str, str]) -> None:
        rows.append({"key": key, "safety": key in SAFETY_KEYS,
                     **{v: entry.get(v) for v in ("en", "ar", "simple_en", "simple_ar")}})

    for prefix, table in (("message", MESSAGES), ("reason", REASONS), ("question", QUESTIONS), ("why", WHY_WE_ASK)):
        for k, entry in table.items():
            add(f"{prefix}.{k}", entry)
    add("rotation_note", ROTATION_NOTE)
    add("how_to_turn_off", HOW_TO_TURN_OFF)
    for moment, variants in ENCOURAGEMENT.items():
        for i, entry in enumerate(variants):
            add(f"encouragement.{moment}.{i}", entry)
    for a in load_actions():
        add(f"action.{a.id}", {"en": a.title.en, "ar": a.title.ar,
                                **({"simple_en": a.simple.en, "simple_ar": a.simple.ar} if a.simple else {})})
    for r in load_recipes():  # dish names: no simple variant
        add(f"recipe.{r.id}", {"en": r.title.en, "ar": r.title.ar})
    return rows
