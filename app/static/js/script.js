class UniversitySimulationForm {
    constructor() {
        this.universities = [
            "University of Lagos",
            "University of Nigeria, Nsukka",
            "Obafemi Awolowo University", 
            "Ahmadu Bello University",
            "Covenant University",
            "Lagos State University"
        ];

        // Initialize element references as null
        this.elements = {
            studentSlider: null,
            studentCount: null,
            numSimulations: null,
            universitySelections: null,
            levelSlider: null,
            levelValue: null,
            form: null
        };
    }

    initialize() {
        // Get all required DOM elements
        this.elements = {
            studentCount: document.getElementById('studentCount'),
            studentSlider: document.getElementById('numStudents'),
            numSimulations: document.getElementById('numSimulations'),
            universitySelections: document.getElementById('universitySelections'),
            levelSlider: document.getElementById('levelSlider'),
            levelValue: document.getElementById('levelValue'),
            form: document.getElementById('simulationForm')
        };

        // Validate that all required elements exist
        for (const [key, element] of Object.entries(this.elements)) {
            if (!element) {
                throw new Error(`Required element "${key}" not found in the DOM`);
            }
        }

        // Initialize event listeners
        this.initializeEventListeners();
        
        // Initialize university selections
        this.updateUniversitySelections();

        // Initialize initial values
        this.updateStudentCount(this.elements.studentSlider.value);
    }

    initializeEventListeners() {
        // Student count slider
        this.elements.studentSlider.addEventListener('input', (e) => 
            this.updateStudentCount(e.target.value)
        );

        // Level slider
        this.elements.levelSlider.addEventListener('input', () => 
            this.handleLevelSliderInput()
        );
        this.elements.levelSlider.addEventListener('change', () => 
            this.handleLevelSliderChange()
        );

        // Number of simulations change
        this.elements.numSimulations.addEventListener('change', () => 
            this.updateUniversitySelections()
        );

        // Form submission
        this.elements.form.addEventListener('submit', (e) => 
            this.handleFormSubmit(e)
        );
    }

    updateStudentCount(value) {
        this.elements.studentCount.textContent = value;
    }

    handleLevelSliderInput() {
        const value = Math.round(this.elements.levelSlider.value / 100) * 100;
        this.elements.levelSlider.value = value;
        this.elements.levelValue.textContent = value;
    }

    handleLevelSliderChange() {
        const value = Math.round(this.elements.levelSlider.value / 100) * 100;
        this.elements.levelSlider.value = value;
        this.elements.levelValue.textContent = value;
    }

    updateUniversitySelections() {
        const numSimulations = parseInt(this.elements.numSimulations.value);
        this.elements.universitySelections.innerHTML = ''; // Clear existing checkboxes
        
        // Create checkbox for each university
        this.universities.forEach((university, index) => {
            const div = document.createElement('div');
            div.className = 'university-option';
            
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.id = `university${index}`;
            checkbox.name = 'universities';
            checkbox.value = university;
            checkbox.addEventListener('change', () => this.validateUniversitySelection());
            
            const label = document.createElement('label');
            label.htmlFor = `university${index}`;
            label.textContent = university;
            
            div.appendChild(checkbox);
            div.appendChild(label);
            this.elements.universitySelections.appendChild(div);
        });

        // Initial validation
        this.validateUniversitySelection();
    }

    validateUniversitySelection() {
        const numSimulations = parseInt(this.elements.numSimulations.value);
        const selectedUniversities = document.querySelectorAll('input[name="universities"]:checked');
        
        let errorDiv = document.getElementById('universityError');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.id = 'universityError';
            errorDiv.className = 'error-message';
            this.elements.universitySelections.appendChild(errorDiv);
        }
        
        if (selectedUniversities.length !== numSimulations) {
            errorDiv.textContent = `Please select exactly ${numSimulations} universit${numSimulations === 1 ? 'y' : 'ies'}`;
            errorDiv.style.display = 'block';
            return false;
        } else {
            errorDiv.style.display = 'none';
            return true;
        }
    }

    async handleFormSubmit(e) {
        e.preventDefault();
        
        if (!this.validateUniversitySelection()) {
            return;
        }
        
        const selectedUniversities = Array.from(
            document.querySelectorAll('input[name="universities"]:checked')
        ).map(checkbox => checkbox.value);
        
        const formData = {
            numStudents: parseInt(this.elements.studentSlider.value),
            numSimulations: parseInt(this.elements.numSimulations.value),
            finalLevel: parseInt(this.elements.levelValue.textContent),
            universities: selectedUniversities
        };

        try {
            const response = await fetch('/form/submit-simulation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            const result = await response.json();
            if (result.status === 'success') {
                window.location.href = result.redirect_url;
            } else {
                console.error(result.message);
                alert('Error: ' + result.message);
            }   
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        }
    }
}

// Make functions globally available for inline HTML event handlers
window.updateStudentCount = function(value) {
    window.simulationForm?.updateStudentCount(value);
};

window.updateUniversitySelections = function() {
    window.simulationForm?.updateUniversitySelections();
};

// Initialize the form handler when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    const simulationFormContainer = document.getElementById("container")
    
    if (simulationFormContainer){
            try {
                const simulationForm = new UniversitySimulationForm();
                simulationForm.initialize();
                window.simulationForm = simulationForm; // Make it accessible globally for inline event handlers
            } catch (error) {
                console.error('Failed to initialize simulation form:', error);
                alert(`Initialization Error: ${error.message}`);
            }
    }
});