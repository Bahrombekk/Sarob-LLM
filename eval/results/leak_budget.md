# O'ylash chegarasida javobga oqish (2026-10-15)

Muammo: o'ylash chegarasi (thinking_token_budget) urilganda vLLM faqat `<channel|>` qo'yardi va model o'ylashni
javob ichida davom ettirardi (foydalanuvchi skrinshoti: rasmdagi tenglama, 512 chegara -> 8192 tokenlik inglizcha monolog).

Yechim: `reasoning_end_str` ga o'tish iborasi — "Time is up. I must stop thinking now and write the final answer
directly, in Uzbek.<channel|>" (vLLM ReasoningConfig buni qo'llab-quvvatlaydi; faqat chegara urilganda qo'shiladi).

| Sinov (qiyin masala, chegara 128, 12 javob) | Oqish |
|---|---|
| Faqat `<channel|>` | 6/12 |
| O'tish iborasi bilan | **0/12** (qayta tekshiruv: 0/16) |

Qo'shimcha: rasmli savollar uchun chegara 512 -> 1024 (filters/filter_tezlik.py).
