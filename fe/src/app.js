document.addEventListener("DOMContentLoaded", () => {
  const weatherSpan = document
    .getElementById("weatherInfo")
    .querySelector("span"); // ID 수정
  const moodText = document.getElementById("moodText");
  const recommendBtn = document.getElementById("recommendFood");
  let selectedMood = "";

  // 날씨 정보 업데이트 함수
  const updateWeather = async (latitude, longitude) => {
    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/api/get_weather/",
        {
          latitude,
          longitude,
        }
      );
      const currentWeather = response.data.weather;
      weatherSpan.textContent = `날씨: ${currentWeather}`;
      return currentWeather;
    } catch (error) {
      console.error("날씨 가져오기 실패:", error);
      weatherSpan.textContent = "날씨: 알 수 없음";
      return "알 수 없음";
    }
  };

  // 위치 정보 가져오기 (기본값: 여수)
  navigator.geolocation.getCurrentPosition(
    (position) => {
      const { latitude, longitude } = position.coords;
      updateWeather(latitude, longitude);
    },
    () => {
      // 위치 정보 없으면 여수 좌표 사용
      const defaultLatitude = 34.7604; // 여수 위도
      const defaultLongitude = 127.6622; // 여수 경도
      weatherSpan.textContent = "날씨: 여수 기준 로딩 중...";
      updateWeather(defaultLatitude, defaultLongitude);
    }
  );

  // 기분 버튼 클릭 이벤트
  document.querySelectorAll(".mood-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      selectedMood = btn.dataset.mood;
      moodText.value = selectedMood;
    });
  });

  // 추천 버튼 클릭 이벤트
  recommendBtn.addEventListener("click", async () => {
    const moodInput = moodText.value || selectedMood;
    if (!moodInput.trim()) {
      alert("기분을 선택하거나 입력해주세요!");
      return;
    }

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords;
        try {
          const weather = await updateWeather(latitude, longitude);
          const foodRes = await axios.post(
            "http://127.0.0.1:8000/recommend_food", // Django URL 수정 필요
            { mood: moodInput, weather }
          );
          const data = foodRes.data;
          localStorage.setItem("recommendResult", JSON.stringify(data));
          window.location.href = "/results.html";
        } catch (error) {
          console.error("추천 오류:", error);
          alert("추천 중 오류 발생!");
        }
      },
      async () => {
        // 위치 정보 없으면 여수 기본값 사용
        const defaultLatitude = 34.7604;
        const defaultLongitude = 127.6622;
        try {
          const weather = await updateWeather(
            defaultLatitude,
            defaultLongitude
          );
          const foodRes = await axios.post(
            "http://127.0.0.1:8000/recommend_food", // Django URL 수정 필요
            { mood: moodInput, weather }
          );
          const data = foodRes.data;
          localStorage.setItem("recommendResult", JSON.stringify(data));
          window.location.href = "/results.html";
        } catch (error) {
          console.error("추천 오류:", error);
          alert("추천 중 오류 발생!");
        }
      }
    );
  });
});
