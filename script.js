// Define the base URL for the API
const API_BASE_URL = "http://127.0.0.1:8000";

// --- Suggestion Logic ---
const suggestButton = document.getElementById('suggestBtn');
const resultDiv = document.getElementById('outfit-result');
suggestButton.addEventListener('click', getSuggestion);

async function getSuggestion() {
    resultDiv.innerHTML = '<p>Getting suggestion...</p>';
    const userId = 1;
    const occasion = 'Casual';
    const apiUrl = `${API_BASE_URL}/suggest/${userId}?occasion=${occasion}`;
    try {
        const response = await fetch(apiUrl);
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to get suggestion');
        }
        const data = await response.json();
        let outfitHtml = `<p>Weather: ${data.current_weather.temperature}°C, ${data.current_weather.condition}</p>
            <div class="item"><strong>Shirt:</strong> ${data.shirt.ItemName} (${data.shirt.Color})</div>
            <div class="item"><strong>Pants:</strong> ${data.pants.ItemName} (${data.pants.Color})</div>
            <div class="item"><strong>Shoes:</strong> ${data.shoes.ItemName} (${data.shoes.Color})</div>`;
        if (data.top) {
            outfitHtml += `<div class="item"><strong>Top:</strong> ${data.top.ItemName} (${data.top.Color})</div>`;
        }
        resultDiv.innerHTML = outfitHtml;
    } catch (error) {
        resultDiv.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
    }
}

// --- Upload & Verify Logic ---
const imageUpload = document.getElementById('image-upload');
const previewContainer = document.getElementById('preview-container');
const previewImage = document.getElementById('preview-image');
const verifyForm = document.getElementById('verify-form');
const uploadStatus = document.getElementById('upload-status');
const submitBtn = document.getElementById('submit-item-btn');

let uploadedFile = null;

imageUpload.addEventListener('change', (event) => {
    uploadedFile = event.target.files[0];
    if (uploadedFile) {
        previewImage.src = URL.createObjectURL(uploadedFile);
        previewContainer.classList.remove('hidden');
        verifyForm.classList.remove('hidden');
        autoTagImage(uploadedFile);
    }
});

async function autoTagImage(file) {
    uploadStatus.innerHTML = '<p>AI is analyzing your image...</p>';
    submitBtn.disabled = true;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const userId = 1;
        const response = await fetch(`${API_BASE_URL}/wardrobe/${userId}/upload-and-tag`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
             const errorData = await response.json();
             throw new Error(errorData.detail || 'Failed to auto-tag');
        }

        const result = await response.json();
        const tags = result.tags;

        // Populate the form with AI suggestions
        document.getElementById('ItemName').value = tags.ItemName;
        document.getElementById('Type').value = tags.Type;
        document.getElementById('Color').value = tags.Color;
        document.getElementById('ColorFamily').value = tags.ColorFamily;
        document.getElementById('Style').value = tags.Style;
        document.getElementById('Pattern').value = tags.Pattern;

        uploadStatus.innerHTML = '<p style="color: green;">AI analysis complete. Please verify the details below.</p>';

    } catch(error) {
        uploadStatus.innerHTML = `<p style="color: red;">Error during AI analysis: ${error.message}</p>`;
    } finally {
        submitBtn.disabled = false;
    }
}

verifyForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    submitBtn.disabled = true;
    uploadStatus.innerHTML = '<p>Adding item to wardrobe...</p>';

    const userId = 1;
    const finalItemData = {
        ItemName: document.getElementById('ItemName').value,
        Type: document.getElementById('Type').value,
        Color: document.getElementById('Color').value,
        ColorFamily: document.getElementById('ColorFamily').value,
        Style: document.getElementById('Style').value,
        Pattern: document.getElementById('Pattern').value,
        MinTemp: parseInt(document.getElementById('MinTemp').value),
        MaxTemp: parseInt(document.getElementById('MaxTemp').value),
        ConditionType: document.getElementById('ConditionType').value,
    };

    const formData = new FormData();
    formData.append('file', uploadedFile);
    formData.append('item_data', JSON.stringify(finalItemData));

    try {
        const response = await fetch(`${API_BASE_URL}/wardrobe/${userId}/add-verified`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
             const errorData = await response.json();
             throw new Error(errorData.detail || 'Failed to add item');
        }

        const result = await response.json();
        uploadStatus.innerHTML = `<p style="color: green;">${result.detail}</p>`;
        verifyForm.classList.add('hidden');
        previewContainer.classList.add('hidden');
        imageUpload.value = '';

    } catch(error) {
        uploadStatus.innerHTML = `<p style="color: red;">Error adding item: ${error.message}</p>`;
    } finally {
        submitBtn.disabled = false;
    }
});