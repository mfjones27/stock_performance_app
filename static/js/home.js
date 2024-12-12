async function confirmTicker(ticker) {
    const data = {
        ticker: ticker
    };

    try {
        const res = await fetch('/confirm_ticker', {
            method: 'POST',
            body: JSON.stringify(data),
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const resData = await res.json();

        if (resData.validity) {
            return true;
        } else {
            throw new Error('Invalid ticker');
        }
    } catch (error) {
        return false;
    }
}

if (window.location.pathname === '/') {
    document.addEventListener('DOMContentLoaded', async () => {
        // Define regex for ticker validation
        const tickerRegex = /^[a-zA-Z]{1,5}$/;

        // Get the compare radio buttons and popup container
        const compareYes = document.getElementById('compare-yes');
        const compareNo = document.getElementById('compare-no');
        const popupContainer = document.getElementById('popupContainer');

        // Show the compare container if "Yes" is selected
        if (compareYes && compareNo && popupContainer) {
            compareYes.addEventListener('change', () => {
                popupContainer.style.display = 'block';

                const submitComparison = document.getElementById('submitComparison');
                const closePopup = document.getElementById('closePopup');
                const comparisonTicker = document.getElementById('comparisonTicker');

                // Hide popup when "Cancel" button is clicked
                closePopup.addEventListener('click', () => {
                    popupContainer.style.display = 'none';
                });

                // Handle ticker submission
                submitComparison.addEventListener('click', async (e) => {
                    e.preventDefault();
                    const ticker = comparisonTicker.value.trim();

                    if (ticker && tickerRegex.test(ticker)) {
                        const comparisonTickerValue = ticker.toUpperCase();
                        const validTicker = await confirmTicker(comparisonTickerValue);

                        if (validTicker) {
                            popupContainer.style.display = 'none';
                        } else {
                            comparisonTicker.style.borderColor = 'red';
                            alert('Ticker was not found. Please enter a valid ticker symbol.');
                        }
                    } else {
                        comparisonTicker.style.borderColor = 'red';
                        alert('Please enter a valid ticker symbol (1-5 alphabetic characters).');
                    }
                });
            });

            // Hide the compare container if "No" is selected
            compareNo.addEventListener('change', () => {
                popupContainer.style.display = 'none';
            });
        }

        // Handle form submission
        const form = document.getElementById('dataForm');
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const mainTicker = document.getElementById('ticker').value.trim().toUpperCase();
            const selectedChartType = document.querySelector('input[name="chart_type"]:checked').value;
            const comparisonChoice = document.querySelector('input[name="compare"]:checked').value;
            const rangeSliderValue = document.getElementById(document.getElementById('date-range').value).textContent; // Assuming this is the selected range value

            // Handle the "Yes" comparison case
            if (comparisonChoice === 'yes') {
                const comparisonTickerV = document.getElementById('comparisonTicker').value.trim().toUpperCase();

                if (!tickerRegex.test(comparisonTickerV)) {
                    alert('Please enter a valid ticker symbol (1-5 alphabetic characters).');
                    return;
                } else if (!await confirmTicker(comparisonTickerV)) {
                    alert('Comparison ticker was not found. Please enter a valid ticker symbol.');
                    return;
                }

                if (tickerRegex.test(mainTicker)) {
                    if (await confirmTicker(mainTicker)) {
                        const data = {
                            mainTicker: mainTicker,
                            chartType: selectedChartType,
                            compare: true,
                            comparisonTicker: comparisonTickerV,
                            range: rangeSliderValue
                        };
                        const resp = await fetch('/get_stock_data', {
                            method: 'POST',
                            body: JSON.stringify(data),
                            headers: {
                                'Content-Type': 'application/json'
                            }
                        });
                        if (resp.ok) {
                            window.location.href = `/stock/${mainTicker}`;
                        } else {
                            alert('Please try again.');
                        }
                    } else {
                        alert('Main ticker was not found. Please enter a valid ticker symbol.');
                    }
                } else {
                    alert('Please enter a valid ticker symbol (1-5 alphabetic characters).');
                }
            }
            // Handle the "No" comparison case
            else if (comparisonChoice === 'no') {
                if (tickerRegex.test(mainTicker)) {
                    if (await confirmTicker(mainTicker)) {
                        const data = {
                            mainTicker: mainTicker,
                            chartType: selectedChartType,
                            compare: false,
                            range: rangeSliderValue
                        };
                        const resp = await fetch('/get_stock_data', {
                            method: 'POST',
                            body: JSON.stringify(data),
                            headers: {
                                'Content-Type': 'application/json'
                            }
                        });
                        if (resp.ok) {
                            window.location.href = `/stock/${mainTicker}`;
                        } else {
                            alert('An error occurred while processing your request.');
                        }
                    } else {
                        alert('Main ticker was not found. Please enter a valid ticker symbol.');
                    }
                } else {
                    alert('Please enter a valid ticker symbol (1-5 alphabetic characters).');
                }
            }
        });
    });
}
