import React from 'react'

export const TatreezPattern: React.FC<{
  width?: number
  height?: number
  style?: React.CSSProperties
  color?: string
  opacity?: number
}> = ({ width = 250, height = 250, style = {}, color = '#2F5A44', opacity = 0.1 }) => {
  const maskId = React.useId()
  const gradId = React.useId()

  return (
    <svg
      aria-hidden="true"
      width={width}
      height={height}
      viewBox="0 0 74 74"
      style={{
        position: 'absolute',
        zIndex: -1,
        pointerEvents: 'none',
        opacity,
        ...style,
      }}
    >
      <defs>
        <radialGradient id={gradId}>
          <stop offset="0" stopColor="#FFFFFF" />
          <stop offset="0.62" stopColor="#FFFFFF" />
          <stop offset="1" stopColor="#FFFFFF" stopOpacity="0" />
        </radialGradient>
        <mask id={maskId}>
          <circle cx="37" cy="42" r="40" fill={`url(#${gradId})`} />
        </mask>
      </defs>
      <g mask={`url(#${maskId})`} fill={color} shapeRendering="crispEdges">
        <path
          transform="translate(0 25)"
          d="M24 0h1v1h-1zM24 1h1v1h-1zM23 2h3v1h-3zM23 3h3v1h-3zM24 4h1v1h-1zM23 5h1v1h-1zM25 5h1v1h-1zM20 6h1v1h-1zM22 6h1v1h-1zM24 6h1v1h-1zM26 6h1v1h-1zM28 6h1v1h-1zM21 7h1v1h-1zM27 7h1v1h-1zM20 8h1v1h-1zM22 8h1v1h-1zM24 8h1v1h-1zM26 8h1v1h-1zM28 8h1v1h-1zM19 9h1v1h-1zM23 9h1v1h-1zM25 9h1v1h-1zM29 9h1v1h-1zM16 10h1v1h-1zM18 10h1v1h-1zM20 10h1v1h-1zM22 10h1v1h-1zM24 10h1v1h-1zM26 10h1v1h-1zM28 10h1v1h-1zM30 10h1v1h-1zM32 10h1v1h-1zM17 11h1v1h-1zM21 11h1v1h-1zM23 11h3v1h-3zM27 11h1v1h-1zM31 11h1v1h-1zM16 12h1v1h-1zM18 12h1v1h-1zM20 12h1v1h-1zM22 12h1v1h-1zM26 12h1v1h-1zM28 12h1v1h-1zM30 12h1v1h-1zM32 12h1v1h-1zM15 13h1v1h-1zM19 13h1v1h-1zM21 13h2v1h-2zM24 13h1v1h-1zM26 13h2v1h-2zM29 13h1v1h-1zM33 13h1v1h-1zM12 14h1v1h-1zM14 14h1v1h-1zM16 14h1v1h-1zM18 14h1v1h-1zM20 14h1v1h-1zM23 14h1v1h-1zM25 14h1v1h-1zM28 14h1v1h-1zM30 14h1v1h-1zM32 14h1v1h-1zM34 14h1v1h-1zM36 14h1v1h-1zM13 15h1v1h-1zM17 15h1v1h-1zM19 15h2v1h-2zM22 15h1v1h-1zM26 15h1v1h-1zM28 15h2v1h-2zM31 15h1v1h-1zM35 15h1v1h-1zM12 16h1v1h-1zM14 16h1v1h-1zM16 16h1v1h-1zM18 16h1v1h-1zM21 16h1v1h-1zM23 16h1v1h-1zM25 16h1v1h-1zM27 16h1v1h-1zM30 16h1v1h-1zM32 16h1v1h-1zM34 16h1v1h-1zM36 16h1v1h-1zM11 17h1v1h-1zM15 17h1v1h-1zM17 17h2v1h-2zM20 17h1v1h-1zM24 17h1v1h-1zM28 17h1v1h-1zM30 17h2v1h-2zM33 17h1v1h-1zM37 17h1v1h-1zM8 18h1v1h-1zM10 18h1v1h-1zM12 18h1v1h-1zM14 18h1v1h-1zM16 18h1v1h-1zM19 18h1v1h-1zM21 18h1v1h-1zM23 18h1v1h-1zM25 18h1v1h-1zM27 18h1v1h-1zM29 18h1v1h-1zM32 18h1v1h-1zM34 18h1v1h-1zM36 18h1v1h-1zM38 18h1v1h-1zM40 18h1v1h-1zM9 19h1v1h-1zM13 19h1v1h-1zM15 19h2v1h-2zM18 19h1v1h-1zM22 19h1v1h-1zM24 19h1v1h-1zM26 19h1v1h-1zM30 19h1v1h-1zM32 19h2v1h-2zM35 19h1v1h-1zM39 19h1v1h-1zM8 20h1v1h-1zM10 20h1v1h-1zM12 20h1v1h-1zM14 20h1v1h-1zM17 20h1v1h-1zM19 20h1v1h-1zM21 20h1v1h-1zM27 20h1v1h-1zM29 20h1v1h-1zM31 20h1v1h-1zM34 20h1v1h-1zM36 20h1v1h-1zM38 20h1v1h-1zM40 20h1v1h-1zM7 21h1v1h-1zM11 21h1v1h-1zM13 21h2v1h-2zM16 21h1v1h-1zM20 21h1v1h-1zM22 21h1v1h-1zM26 21h1v1h-1zM28 21h1v1h-1zM32 21h1v1h-1zM34 21h2v1h-2zM37 21h1v1h-1zM41 21h1v1h-1zM4 22h1v1h-1zM6 22h1v1h-1zM8 22h1v1h-1zM10 22h1v1h-1zM12 22h1v1h-1zM15 22h1v1h-1zM17 22h1v1h-1zM19 22h1v1h-1zM24 22h1v1h-1zM29 22h1v1h-1zM31 22h1v1h-1zM33 22h1v1h-1zM36 22h1v1h-1zM38 22h1v1h-1zM40 22h1v1h-1zM42 22h1v1h-1zM44 22h1v1h-1zM2 23h2v1h-2zM5 23h1v1h-1zM9 23h1v1h-1zM11 23h2v1h-2zM14 23h1v1h-1zM18 23h1v1h-1zM20 23h1v1h-1zM24 23h1v1h-1zM28 23h1v1h-1zM30 23h1v1h-1zM34 23h1v1h-1zM36 23h2v1h-2zM39 23h1v1h-1zM43 23h1v1h-1zM45 23h2v1h-2zM0 24h5v1h-5zM6 24h1v1h-1zM8 24h1v1h-1zM10 24h1v1h-1zM13 24h1v1h-1zM15 24h1v1h-1zM17 24h1v1h-1zM22 24h5v1h-5zM31 24h1v1h-1zM33 24h1v1h-1zM35 24h1v1h-1zM38 24h1v1h-1zM40 24h1v1h-1zM42 24h1v1h-1zM44 24h5v1h-5z"
        />
      </g>
    </svg>
  )
}

export const ArabicCalligraphyRing: React.FC<{
  width?: number
  height?: number
  style?: React.CSSProperties
  color?: string
  opacity?: number
}> = ({ width = 460, height = 460, style = {}, color = '#4F7A62', opacity = 0.14 }) => {
  const maskId = React.useId()
  const gradId = React.useId()

  return (
    <svg
      aria-hidden="true"
      width={width}
      height={height}
      viewBox="0 0 460 460"
      style={{
        position: 'absolute',
        zIndex: -1,
        pointerEvents: 'none',
        opacity,
        ...style,
      }}
    >
      <defs>
        <radialGradient id={gradId}>
          <stop offset="0" stopColor="#FFFFFF" />
          <stop offset="0.5" stopColor="#FFFFFF" stopOpacity="0.9" />
          <stop offset="1" stopColor="#FFFFFF" stopOpacity="0" />
        </radialGradient>
        <mask id={maskId}>
          <circle cx="230" cy="230" r="230" fill={`url(#${gradId})`} />
        </mask>
      </defs>
      <g
        mask={`url(#${maskId})`}
        fill={color}
        fontFamily="'Aref Ruqaa', serif"
        fontWeight="700"
        textAnchor="middle"
        dominantBaseline="central"
      >
        <text transform="translate(248 230) rotate(-57)" fontSize="72">صحة</text>
        <text transform="translate(207 250) rotate(-38)" fontSize="49">سلام</text>
        <text transform="translate(233 192) rotate(-10)" fontSize="64">حياة</text>
        <text transform="translate(259 266) rotate(156)" fontSize="67">قوة</text>
        <text transform="translate(177 221) rotate(-36)" fontSize="69">راحة</text>
        <text transform="translate(280 200) rotate(-35)" fontSize="68">عافية</text>
        <text transform="translate(213 290) rotate(15)" fontSize="44">بداية</text>
        <text transform="translate(198 171) rotate(13)" fontSize="67">ثبات</text>
        <text transform="translate(299 254) rotate(70)" fontSize="62">أمل</text>
        <text transform="translate(158 258) rotate(48)" fontSize="59">سلام</text>
        <text transform="translate(265 159) rotate(10)" fontSize="60">عودة</text>
        <text transform="translate(256 308) rotate(-67)" fontSize="41">قوة</text>
        <text transform="translate(153 187) rotate(-9)" fontSize="63">حياة</text>
        <text transform="translate(321 211) rotate(57)" fontSize="58">أمل</text>
        <text transform="translate(175 305) rotate(-36)" fontSize="41">سلام</text>
        <text transform="translate(217 135) rotate(55)" fontSize="55">حياة</text>
        <text transform="translate(308 293) rotate(73)" fontSize="59">بداية</text>
        <text transform="translate(125 234) rotate(-46)" fontSize="57">طاقة</text>
        <text transform="translate(307 157) rotate(65)" fontSize="49">صحة</text>
        <text transform="translate(225 337) rotate(-8)" fontSize="48">خطوة</text>
        <text transform="translate(157 146) rotate(-30)" fontSize="59">حياة</text>
        <text transform="translate(346 245) rotate(-70)" fontSize="45">صبر</text>
        <text transform="translate(132 296) rotate(-29)" fontSize="47">طاقة</text>
        <text transform="translate(257 115) rotate(33)" fontSize="38">عودة</text>
        <text transform="translate(292 334) rotate(57)" fontSize="52">سلام</text>
        <text transform="translate(109 193) rotate(37)" fontSize="57">حياة</text>
        <text transform="translate(348 178) rotate(55)" fontSize="41">أمل</text>
        <text transform="translate(179 347) rotate(-14)" fontSize="55">طاقة</text>
        <text transform="translate(184 108) rotate(24)" fontSize="49">نية</text>
        <text transform="translate(351 291) rotate(-45)" fontSize="48">خطوة</text>
        <text transform="translate(95 264) rotate(26)" fontSize="56">حياة</text>
        <text transform="translate(307 116) rotate(-46)" fontSize="52">صبر</text>
        <text transform="translate(254 366) rotate(-5)" fontSize="39">نور</text>
        <text transform="translate(115 144) rotate(7)" fontSize="54">عودة</text>
        <text transform="translate(378 218) rotate(-12)" fontSize="45">قوة</text>
        <text transform="translate(128 336) rotate(81)" fontSize="47">راحة</text>
        <text transform="translate(231 84) rotate(-27)" fontSize="41">عودة</text>
        <text transform="translate(334 340) rotate(35)" fontSize="46">بداية</text>
        <text transform="translate(74 216) rotate(25)" fontSize="37">شكر</text>
        <text transform="translate(356 138) rotate(6)" fontSize="40">صبر</text>
        <text transform="translate(201 382) rotate(52)" fontSize="48">راحة</text>
        <text transform="translate(143 98) rotate(75)" fontSize="43">نية</text>
        <text transform="translate(389 272) rotate(97)" fontSize="40">سلام</text>
        <text transform="translate(82 303) rotate(-13)" fontSize="46">شكر</text>
        <text transform="translate(289 78) rotate(-54)" fontSize="41">أمل</text>
        <text transform="translate(294 381) rotate(9)" fontSize="39">طاقة</text>
        <text transform="translate(75 159) rotate(28)" fontSize="47">عودة</text>
        <text transform="translate(396 181) rotate(68)" fontSize="44">هدوء</text>
      </g>
    </svg>
  )
}
