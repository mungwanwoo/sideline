document.addEventListener("DOMContentLoaded", () => {
    const weatherSpan = document.getElementById("weatherText");

    navigator.geolocation.getCurrentPosition(async (position) => {
        const { latitude, longitude } = position.coords;

        try {
            const response = await axios.post("http://127.0.0.1:8000/get_weather/", {
                latitude,
                longitude,
            });

            const currentWeather = response.data.weather;
            weatherSpan.textContent = `날씨: ${currentWeather}`;
        } catch (error) {
            console.error("날씨 가져오기 실패:", error);
            weatherSpan.textContent = "날씨: 알 수 없음";
        }
    }, () => {
        weatherSpan.textContent = "날씨: 위치 정보 없음";
    });

    // 나머지 기존 이벤트 핸들러 (예: 버튼 클릭, 추천 등)는 여기 아래에 계속 쓰시면 됩니다.
});

document.addEventListener("DOMContentLoaded", () => {
    let selectedMood = "";

    // 기분 버튼 클릭 이벤트
    document.querySelectorAll(".mood-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            selectedMood = btn.dataset.mood;
            document.getElementById("moodText").value = selectedMood;
        });
    });

    // 추천 버튼 클릭
    document.getElementById("recommendFood").addEventListener("click", async () => {
        const moodInput = document.getElementById("moodText").value || selectedMood;
        if (!moodInput) {
            alert("기분을 선택하거나 입력해주세요.");
            return;
        }

        // 위치 정보 가져오기
        navigator.geolocation.getCurrentPosition(async (position) => {
            const { latitude, longitude } = position.coords;

            try {
                // 날씨 가져오기 (FastAPI 호출)
                const weatherRes = await axios.post("http://YOUR_FASTAPI_URL/get_weather/", {
                    latitude,
                    longitude
                });
                const weather = weatherRes.data.weather || "맑음";

                // 추천 음식 가져오기 (Django 호출)
                const foodRes = await axios.post("http://YOUR_DJANGO_URL/recommend_food", {
                    mood: moodInput,
                    weather: weather
                });

                const data = foodRes.data;

                // 로컬스토리지에 데이터 저장 후 결과 페이지로 이동
                localStorage.setItem("recommendResult", JSON.stringify(data));
                window.location.href = "/results.html";

            } catch (error) {
                console.error("에러 발생:", error);
                alert("추천을 불러오는 중 오류가 발생했습니다.");
            }

        }, () => {
            alert("위치 정보를 허용해주세요.");
        });
    });
});

document.addEventListener("DOMContentLoaded", () => {
    const recommendBtn = document.getElementById("recommendFood");

    recommendBtn.addEventListener("click", async () => {
        const text = document.getElementById("moodText").value;

        if (!text.trim()) {
            alert("기분을 입력해주세요!");
            return;
        }

        navigator.geolocation.getCurrentPosition(async (position) => {
            const { latitude, longitude } = position.coords;

            try {
                // 1. 날씨 먼저 요청
                const weatherRes = await axios.post("http://YOUR_FASTAPI_URL/get_weather/", {
                    latitude,
                    longitude
                });
                const weather = weatherRes.data.weather;

                // 2. 텍스트 + 날씨로 감정 분석 + 음식 추천 요청
                const llmRes = await axios.post("http://YOUR_FASTAPI_URL/analyze-llm", {
                    text,
                    weather
                });

                // 결과 받아오기
                const result = llmRes.data;

                // 3. result.html로 이동하면서 데이터 전달
                // 방법 1: localStorage 사용
                localStorage.setItem("recommend_result", JSON.stringify(result));
                window.location.href = "/recommend.html";

            } catch (error) {
                console.error("에러:", error);
                alert("추천 요청 중 오류 발생!");
            }

        }, (err) => {
            console.error("위치 오류:", err);
            alert("위치 정보를 가져올 수 없습니다.");
        });
    });
});
