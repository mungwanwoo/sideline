const express = require("express");
const path = require("path");
const app = express();

// 'republic' 폴더를 정적 파일 경로로 설정 (index.html이 있는 곳)
app.use(express.static(path.join(__dirname, "public")));

// 'src' 폴더를 정적 파일 경로로 설정 (app.js가 있는 곳)
app.use("/src", express.static(path.join(__dirname, "src")));

// 기본 경로로 index.html을 제공
app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

app.listen(3000, () => console.log("서버 실행: http://localhost:3000"));
