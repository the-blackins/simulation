function updateStudentCount(value) {
    document.getElementById('studentCount').textContent = value;
}

output = document.getElementById('levelValue')

const slider = document.getElementById('levelSlider');
slider.oninput = function() {
    // Round to nearest 100
    const value = Math.round(this.value / 100) * 100;
    this.value = value;
    output.textContent = value; 
}
    // Add snap effect and send data to backend
slider.onchange = function() {
    const value = Math.round(this.value / 100) * 100;
    this.value = value;
    output.textContent = value;
}

document.getElementById('simulationForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        numStudents: parseInt(document.getElementById('numStudents').value),
        numSimulations: parseInt(document.getElementById('numSimulations').value),
        finalLevel: parseInt(document.getElementById('levelValue').textContent)
    };

    try {
        const response = await fetch('/api/submit-simulation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const result = await response.json();
        if (result.status === 'success') {
            alert('Simulation configuration submitted successfully!');
            // Here you can add code to redirect or update the UI
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while submitting the form.');
    }
}); 