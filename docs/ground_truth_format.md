## 🏅 Ground Truth Dataset Format

Each line in `data/ground_truth/ground_truth_dataset.jsonl` should be a JSON object like:

```json
{"chunk_id": "cd61606a-b53b-5385-b764-1b82a8d660ec", 
  "topic": "moon", 
  "text": "Commercial Lunar Payload Services (CLPS) is a NASA program to hire companies to send small robotic landers and rovers to the Moon. Most landing sites are near the lunar south pole where they will scout for lunar resources, test in situ resource utilization (ISRU) concepts, and perform lunar science to support the Artemis lunar program. CLPS is intended to buy end-to-end payload services between Earth and the lunar surface using fixed-price contracts. The program achieved the first landing on the Moon by a commercial company in history with the IM-1 mission in 2024. The program was extended to add support for large payloads starting after 2025.\nThe CLPS program is run by NASA's Science Mission Directorate along with the Human Exploration and Operations and Space Technology Mission directorates.", 
  "level": "Middle School", 
  "question": "What is the purpose of the Commercial Lunar Payload Services (CLPS) program?", 
  "answer": "The purpose of the CLPS program is to hire companies to send small robotic landers and rovers to the Moon."
}
```