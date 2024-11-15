const universities = [
    "University of Lagos",
    "University of Nigeria, Nsukka",
    "Obafemi Awolowo University",
    "Ahmadu Bello University",
    "Covenant University",
    "Lagos State University"
];

function updateStudentCount(value) {
    document.getElementById('studentCount').textContent = value;
}

function updateUniversitySelections() {
    const numSimulations = parseInt(document.getElementById('numSimulations').value);
    const container = document.getElementById('universitySelections');
    container.innerHTML = ''; // Clear existing checkboxes
    
    // Create checkbox for each university
    universities.forEach((university, index) => {
        const div = document.createElement('div');
        div.className = 'university-option';
        
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = `university${index}`;
        checkbox.name = 'universities';
        checkbox.value = university;
        checkbox.addEventListener('change', () => validateUniversitySelection());
        
        const label = document.createElement('label');
        label.htmlFor = `university${index}`;
        label.textContent = university;
        
        div.appendChild(checkbox);
        div.appendChild(label);
        container.appendChild(div);
    });
}

function validateUniversitySelection() {
    const numSimulations = parseInt(document.getElementById('numSimulations').value);
    const selectedUniversities = document.querySelectorAll('input[name="universities"]:checked');
    const errorDiv = document.getElementById('universityError') || document.createElement('div');
    errorDiv.id = 'universityError';
    errorDiv.className = 'error-message';
    
    if (selectedUniversities.length !== numSimulations) {
        errorDiv.textContent = `Please select exactly ${numSimulations} universit${numSimulations === 1 ? 'y' : 'ies'}`;
        errorDiv.style.display = 'block';
        document.getElementById('universitySelections').appendChild(errorDiv);
        return false;
    } else {
        errorDiv.style.display = 'none';
        return true;
    }
}

const output = document.getElementById('levelValue');
const slider = document.getElementById('levelSlider');

slider.oninput = function() {
    const value = Math.round(this.value / 100) * 100;
    this.value = value;
    output.textContent = value;
}

slider.onchange = function() {
    const value = Math.round(this.value / 100) * 100;
    this.value = value;
    output.textContent = value;
}

document.getElementById('simulationForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    if (!validateUniversitySelection()) {
        return;
    }
    
    const selectedUniversities = Array.from(document.querySelectorAll('input[name="universities"]:checked'))
        .map(checkbox => checkbox.value);
    
    const formData = {
        numStudents: parseInt(document.getElementById('numStudents').value),
        numSimulations: parseInt(document.getElementById('numSimulations').value),
        finalLevel: parseInt(document.getElementById('levelValue').textContent),
        universities: selectedUniversities
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
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while submitting the form.');
    }
});

// Initialize university selections when page loads
document.addEventListener('DOMContentLoaded', updateUniversitySelections);