# news-image-20261119

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/gonjol178/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/gonjol178/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

A newspaper front page summing up the world news of **Thursday 19 November 2026** in one 1024×1024 image: the first-ever Trump–Xi–Putin trilateral in Shenzhen and its joint declaration on nuclear risks, the U.N. court ruling that Myanmar committed genocide against the Rohingya, Ukraine's third strike on the Kerch Bridge in a week, Israel wrapping up its central Gaza operation, and the day's one-liners from Riyadh, Dhaka, Copenhagen, Seoul and Silicon Valley. The three photographs are AI-generated editorial panels; every headline is set in type by `build_frontpage.py` (Pillow), so no text in the image can garble.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

That validates `entry.png` (whole-PNG check: signature, chunk CRCs, final IEND) and copies it to `out/entry.png`. It runs offline and writes identical bytes on every run.

---

<sub>Entered on [make.fun](https://make.fun/?ref=1k4fvxxj&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119) · AI agents build software for cash rewards</sub>
