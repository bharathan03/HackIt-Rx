// server.js
import express from "express";
import bodyParser from "body-parser";
import fetch from "node-fetch";
import dotenv from "dotenv";

dotenv.config();

const app = express();
app.use(bodyParser.json());

const GEMINI_API_KEY = process.env.GEMINI_API_KEY;

app.post("/translate", async (req, res) => {
  try {
    const { text, targetLang } = req.body;

    // Call Gemini API
    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key=${GEMINI_API_KEY}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          contents: [
            {
              role: "user",
              parts: [{ text: `Translate this into ${targetLang}: ${text}` }]
            }
          ]
        }),
      }
    );

    const data = await response.json();

    // Check if response contains translation
    if (data.candidates && data.candidates[0]?.content?.parts[0]?.text) {
      res.json({ translation: data.candidates[0].content.parts[0].text });
    } else {
      console.error("Gemini response error:", data);
      res.status(500).json({ error: "No translation received" });
    }

  } catch (error) {
    console.error("Server error:", error);
    res.status(500).json({ error: "Translation failed" });
  }
});

app.listen(3000, () => console.log("Gemini translation server running at http://localhost:3000"));
