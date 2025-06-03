
// import Chart from 'chart.js/auto';
class StudentSimulation {
    constructor() {
        this.simulationInterval = null;
        this.performanceChart = null;
        this.factorsChart = null;
        this.chartConfig = {
            performance: {
                type: 'line',
                data: {
                    labels: [],
                    datasets: []
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Student Performance Over Time'
                        }
                    },
                    scales: {
                        y: {
                            min: 0,
                            max: 100
                        }
                    }
                }
            },
            factors: {
                type: 'line',
                data: {
                    labels: [],
                    datasets: []
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Factor Impact Analysis'
                        }
                    },
                    scales: {
                        y: {
                            min: 0,
                            max: 100
                        }
                    }
                }
            }
        };
    }

    
    initialize(chartData) {
        // Get canvas contexts
        const container = document.getElementById("container");
        // const performanceCanvas = document.getElementById('performanceChart');
        // const factorsCanvas = document.getElementById('factorsChart');

        // Initialize charts
        for (let i = 0; i < chartData.length; i++) {
            let div = document.createElement('div');
            div.className = "canvas-container";

            let canvas = document.createElement('canvas')
            canvas.id = "canvas" + i;
            div.appendChild(canvas);

            let factorsCanvas = document.createElement('canvas')
            factorsCanvas.id = "factor-canvas" + i;
            div.appendChild(factorsCanvas)

            
            container.appendChild(div)

            if (!canvas || !factorsCanvas) {
                console.error('Canvas elements not found');
                return;
            }
            const performanceCanvas = document.getElementById(`${canvas.id}`);
            this.performanceChart = new Chart(
                performanceCanvas.getContext('2d'),
                this.chartConfig.performance,
                this.chartConfig.performance.options.plugins.title.text = `Simulation ID ${chartData[i].simulation_id}    ${chartData[i].university}`
            );
            const factorCanvas = document.getElementById(`${factorsCanvas.id}`);
            this.factorsChart = new Chart(
            factorCanvas.getContext('2d'),
            this.chartConfig.factors
        );
        }


        

        // Bind event listeners
        this.bindEventListeners();
    }


    bindEventListeners() {
        const startBtn = document.getElementById('startBtn');
        const pauseBtn = document.getElementById('pauseBtn');
        const resetBtn = document.getElementById('resetBtn');

        if (!startBtn || !pauseBtn || !resetBtn) {
            console.error('Control buttons not found');
            return;
        }

        startBtn.addEventListener('click', () => this.startSimulation());
        pauseBtn.addEventListener('click', () => this.pauseSimulation());
        resetBtn.addEventListener('click', () => this.resetSimulation());
    }

    startSimulation() {
        const startBtn = document.getElementById('startBtn');
        const pauseBtn = document.getElementById('pauseBtn');
        const status = document.getElementById('status');

        if (startBtn) startBtn.disabled = true;
        if (pauseBtn) pauseBtn.disabled = false;
        if (status) status.textContent = 'Status: Running';
        
        // Clear any existing interval
        if (this.simulationInterval) {
            clearInterval(this.simulationInterval);
        }
        
        // Run first step immediately
        this.runSimulationStep();
        
        // Then set up interval
        this.simulationInterval = setInterval(() => this.runSimulationStep(), 2000);
    }

    pauseSimulation() {
        const startBtn = document.getElementById('startBtn');
        const pauseBtn = document.getElementById('pauseBtn');
        const status = document.getElementById('status');

        if (startBtn) startBtn.disabled = false;
        if (pauseBtn) pauseBtn.disabled = true;
        if (status) status.textContent = 'Status: Paused';
        
        if (this.simulationInterval) {
            clearInterval(this.simulationInterval);
            this.simulationInterval = null;
        }
    }

    resetSimulation() {
        this.pauseSimulation();
        
        // Reset chart data
        if (this.performanceChart) {
            this.performanceChart.data.labels = [];
            this.performanceChart.data.datasets = [];
            this.performanceChart.update();
        }
        
        if (this.factorsChart) {
            this.factorsChart.data.datasets = [];
            this.factorsChart.update();
        }
        
        const status = document.getElementById('status');
        if (status) status.textContent = 'Status: Reset';
    }

    async runSimulationStep() {
        try {
            const response = await fetch('/simulation/api/run_step', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin',
                body: JSON.stringify({}) // Add empty body for POST request
            });

            if (!response.ok) {
                console.log(response.json())
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            console.log(data)
            
            if (data.status === 'success') {
                this.updateCharts(data.results);
                
            } else {
                console.error('Simulation step failed:', data.error);
                this.pauseSimulation();
            }
        } catch (error) {
            console.error('Simulation step error:', error);
            this.pauseSimulation();
            
            // Update status to show error
            const status = document.getElementById('status');
            if (status) status.textContent = `Status: Error - ${error.message}`;
        }
    }

    updateCharts(results) {
        if (!results || !results.length) {
            console.error('No results to update charts');
            return;
        }

        const timestamp = new Date().toLocaleTimeString();
        
        // Update performance chart
        if (this.performanceChart) {
            if (this.performanceChart.data.labels.length > 20) {
                this.performanceChart.data.labels.shift();
                this.performanceChart.data.datasets.forEach(dataset => dataset.data.shift());
            }
            
            this.performanceChart.data.labels.push(timestamp);
            
            results.forEach(result => {
                let dataset = this.performanceChart.data.datasets.find(
                    ds => ds.label === `Student ${result.student_id}`
                );
                
                if (!dataset) {
                    dataset = {
                        label: `Student ${result.student_id}`,
                        data: [],
                        borderColor: `hsl(${result.student_id * 137.508}deg, 70%, 50%)`,
                        tension: 0.4
                    };
                    this.performanceChart.data.datasets.push(dataset);
                }
                
                dataset.data.push(result.score);
            });
            
            this.performanceChart.update();
        }
    }
} webkitURL;                                                                                                                                                  




// Initialize simulation when DOM is loaded
document.addEventListener('DOMContentLoaded' , async() => {
    try {
        const response = await fetch('/simulation/api/chart_render');  
        const chartDataInit = await response.json();
        

        const dataArray = chartDataInit.data; // Extract the array
        if (!Array.isArray(dataArray)) {
            console.error("Extracted dataArray is not an array", dataArray);
        } else {
            const chartData = dataArray.map(item => item);
            console.log(chartData)
            const simulation = new StudentSimulation();

            simulation.initialize(chartData);
            console.log('Simulation initialized successfully');
            
        }
                
        
    } catch (error) {
        console.error('Failed to initialize simulation:', error);
        const status = document.getElementById('status');
        if (status) status.textContent = `Error: ${error.message}`;
    }
});
