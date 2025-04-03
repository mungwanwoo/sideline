let latitude, longitude;
let weather = null;

document.addEventListener('DOMContentLoaded', () => {
    if (!navigator.geolocation) {
        alert('이 브라우저는 Geolocation을 지원하지 않습니다.');
        document.getElementById('weatherInfo').textContent = '날씨: 지원 불가';
        return;
    }

    navigator.geolocation.getCurrentPosition(
        async (position) => {
            latitude = position.coords.latitude;
            longitude = position.coords.longitude;
            const weatherResponse = await axios.post('http://localhost:8000/get-weather', { latitude, longitude });
            weather = weatherResponse.data.weather;
            document.getElementById('weatherInfo').textContent = `날씨: ${weather}`;
        },
        (error) => {
            alert('위치 가져오기 실패. 기본 위치(서울) 사용.');
            latitude = 37.5665;
            longitude = 126.9780;
            axios.post('http://localhost:8000/get-weather', { latitude, longitude }).then(response => {
                weather = response.data.weather;
                document.getElementById('weatherInfo').textContent = `날씨: ${weather}`;
            });
        }
    );

    document.querySelectorAll('.mood-btn').forEach(button => {
        button.addEventListener('click', () => {
            document.querySelectorAll('.mood-btn').forEach(btn => btn.classList.remove('bg-blue-300'));
            button.classList.add('bg-blue-300');
        });
    });
});

document.getElementById('recommendFood').addEventListener('click', async () => {
    if (!latitude || !longitude || !weather) {
        alert('위치와 날씨 정보를 가져오는 중입니다. 잠시 후 다시 시도해주세요.');
        return;
    }

    let mood = null;
    const moodButtons = document.querySelectorAll('.mood-btn');
    moodButtons.forEach(button => {
        if (button.classList.contains('bg-blue-300')) {
            mood = button.dataset.mood;
        }
    });

    if (!mood && document.getElementById('moodText').value) {
        const text = document.getElementById('moodText').value;
        const moodResponse = await axios.post('http://localhost:8000/analyze-mood', { text });
        mood = moodResponse.data.emotion;
    } else if (!mood) {
        alert('기분을 선택하거나 텍스트로 입력해주세요.');
        return;
    }

    const recommendResponse = await axios.post('http://localhost:8001/api/recommend/', {
        mood: mood,
        weather: weather
    });

    const { food, recommendations } = recommendResponse.data;
    const recommendationSection = document.getElementById('recommendation');
    recommendationSection.style.display = 'block';
    const foodList = document.getElementById('foodListItems');
    const displayedRecommendations = recommendations.slice(0, 3);
    foodList.innerHTML = displayedRecommendations.map(rec => `
        <div class="bg-white p-4 rounded-lg shadow-md text-center">
            <img src="https://via.placeholder.com/200" class="w-full h-40 object-cover rounded-md">
            <h3 class="font-semibold mt-2">${rec.name}</h3>
            <p class="text-gray-600">${rec.details || '추천 이유가 없습니다.'}</p>
        </div>
    `).join('');
});