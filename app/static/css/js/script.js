function updateStudentCount(value) {
    document.getElementById('studentCount').textContent = value;
}

document.getElementById('simulationForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        numStudents: parseInt(document.getElementById('numStudents').value),
        numSimulations: parseInt(document.getElementById('numSimulations').value)
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