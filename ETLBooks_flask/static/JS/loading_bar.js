document.addEventListener('DOMContentLoaded', function() {
    const cancelScraperBtn = document.getElementById("cancelScraperBtn")
    const prepareScraperBtn = document.getElementById('prepareScraperBtn');
    const startScrapingBtn = document.getElementById('startScrapingBtn');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const progressBar = document.getElementById('progressBar');
    let progressInterval;

    
    function resetProgressBar() {
        progressBar.style.width = '0%';
        progressBar.innerHTML = '';
    }

    function updateProgressBar(percentage) {
        
        progressBar.style.width = percentage + '%';
        progressBar.innerHTML = percentage + '%';
    }

    function checkProgress(){
        fetch("scraper/get_progress")
        .then(response => response.json())
        .then(data => {
            if (data.progress != undefined) {
                updateProgressBar(data.progress);

                if (data.progress >= 100) {
                    clearInterval(progressInterval);
                }
            }
        })
        .catch(error => {
            console.error('Error checking progress:', error);    
        })
    }

    // Button click event for "Prepare Scraper"
    prepareScraperBtn.addEventListener('click', function() {
        prepareScraperBtn.disabled = true;
        prepareScraperBtn.style.display = 'none';
        loadingSpinner.style.display = 'block';
        resetProgressBar();
        
        fetch('/scraper/prepare_scraper')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Preparation complete! Total books to scrape: ' + data.total_books);
                    startScrapingBtn.disabled = false;
                    startScrapingBtn.style.display = 'block';
                    loadingSpinner.style.display = 'none';
                } else {
                    alert('Failed to prepare scraper.');
                    prepareScraperBtn.disabled = false;
                    prepareScraperBtn.style.display = 'block';
                    loadingSpinner.style.display = 'none';
                }
            })
            .catch(error => {
                console.error('Error during preparation:', error);
                alert('An error occurred during preparation.');
                loadingSpinner.style.display = 'none';
                prepareScraperBtn.style.display = 'block';
                prepareScraperBtn.disabled = false
            });
    });

    // Button click event for "Start Scraping"
    startScrapingBtn.addEventListener('click', function() {
        startScrapingBtn.disabled = true;
        startScrapingBtn.style.display = 'none';
        cancelScraperBtn.style.display= "block";
        cancelScraperBtn.disabled = false 
        progressInterval=setInterval(checkProgress, 1000);
        fetch('/scraper/start_scraper')
            .then(response => response.json())
            .then(data => {   
                if (data.success) {
                    alert('Scraping completed!Return to home to see the books!');
                    clearInterval(progressInterval);
                    fetch('/scraper/update_graphs', { method: 'POST' });
                    fetch('/analyse/update_comments', { method: 'POST' });
                    
                } else {
                    alert('An error occurred during scraping.');
                    fetch('/scraper/update_graphs', { method: 'POST' });
                    fetch('/analyse/update_comments', { method: 'POST' });
                }

                // Re-enable the "Prepare Scraper" button after the process
                prepareScraperBtn.disabled = false;
                prepareScraperBtn.style.display = 'block';
            })
            .catch(error => {
                console.error('Error during scraping:', error);
                alert('An error occurred during scraping.');
                startScrapingBtn.disabled = false;
                startScrapingBtn.style.display = 'block';
                clearInterval(progressInterval);
            });
    });
    cancelScraperBtn.addEventListener('click', function() {
        // Send a request to cancel the scraping operation
        fetch('/scraper/cancel_scraping', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    clearInterval(progressInterval);
                    resetProgressBar();
                    cancelScraperBtn.style.display = 'none';
                    cancelScraperBtn.disabled= true;
                    fetch('/scraper/update_graphs', { method: 'POST' });
                    fetch('/analyse/update_comments', { method: 'POST' });
                    alert('Scraping has been cancelled.');
                } else {
                    alert('An error occurred while cancelling the scraping.');
                }
            })
            .catch(error => {
                console.error('Error during cancellation:', error);
                alert('An error occurred while cancelling the scraping.');
            });
        prepareScraperBtn.disabled = false;
        prepareScraperBtn.style.display = 'block';
    });
});