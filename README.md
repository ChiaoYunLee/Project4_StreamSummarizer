### Stream Summarizer: Elevating Video Editing Through Text Mining
#### | Course Project: Text Mining Applications in Business (2023.Senior)

#### | 👾 Intro.
Stream Summarizer, your reliable tool built with Python for simplifying video editing. Equipped with features like keyword extraction, emotion analysis, and emoji interpretation, StreamSummarizer enables video editors to quickly spot the most engaging, crucial, or amusing segments in live streams without needing to watch them entirely,streamline their editing process, and save their valuable time and effort. 

#### | ✂️ How It Works
Stream Summarizer is your go-to solution for efficient video editing. To begin with, it will first filter out segments (30 second/segment) from the live stream which have more comments than average. Then, it will perform keyword extraction (TF-IDF), emotion analysis(LeXmo), and emoji interpretation (emosent) on these segments, consolidating the analytical results from each segment. This way, video editors can gain an understanding of the segment's content and gauge audience engagement, helping them decide whether to include the segment in their edited video.

#### | 🌟 Key Features
- Text Preprocessing: Transform common slangs used in live stream context into words or sentences that can be analyzed. e.g. ganba -> do your best 
- Keyword Extraction: Identify critical topics and moments through finding words that appear more than 5 times in each segment's comments.
- Emotion Insights: Understand the emotional context of comments to pinpoint impactful segments (emotion score > 0.08).
- Emoji Analysis: Decode the emojis to discover funny, exciting, or noteworthy segments of the video. e.g.🤣 = "Rolling on Floor Laughing"

#### | 🛠️ Techniques: Python
#### | 👩🏻‍💻 My Role: Text Preprocessing & Emotion Analysis
