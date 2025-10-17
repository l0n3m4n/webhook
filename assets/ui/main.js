document.addEventListener('DOMContentLoaded', () => {
    // Theme Switcher
    const themeButtons = document.querySelectorAll('.theme-btn');
    const currentTheme = localStorage.getItem('theme') || 'hacker';
    document.body.className = currentTheme + '-theme';

    themeButtons.forEach(button => {
        if (button.dataset.theme === currentTheme) {
            button.classList.add('active');
        }
        button.addEventListener('click', (e) => {
            const selectedTheme = e.currentTarget.dataset.theme;
            document.body.className = selectedTheme + '-theme';
            localStorage.setItem('theme', selectedTheme);

            // Update active state
            themeButtons.forEach(btn => btn.classList.remove('active'));
            e.currentTarget.classList.add('active');
        });
    });

    // File Search/Filter
    const searchBox = document.getElementById('search-box');
    const fileList = document.getElementById('file-list').getElementsByTagName('tbody')[0];
    const fileRows = fileList.getElementsByTagName('tr');

    searchBox.addEventListener('keyup', () => {
        const query = searchBox.value.toLowerCase();
        for (let i = 0; i < fileRows.length; i++) {
            const fileName = fileRows[i].getElementsByTagName('td')[0].textContent.toLowerCase();
            if (fileName.includes(query)) {
                fileRows[i].style.display = '';
            } else {
                fileRows[i].style.display = 'none';
            }
        }
    });

    // Copy URL to Clipboard
    const copyButtons = document.querySelectorAll('.copy-btn');
    copyButtons.forEach(button => {
        button.addEventListener('click', () => {
            const fileUrl = button.getAttribute('data-url');
            const fullUrl = new URL(fileUrl, window.location.href).href;
            navigator.clipboard.writeText(fullUrl).then(() => {
                const originalText = button.textContent;
                button.textContent = 'Copied!';
                setTimeout(() => {
                    button.textContent = originalText;
                }, 2000);
            }).catch(err => {
                console.error('Failed to copy URL: ', err);
            });
        });
    });

    // File Preview Modal
    const modal = document.getElementById('preview-modal');
    const closeBtn = document.querySelector('.close-btn');
    const previewContent = document.getElementById('preview-content');
    const fileLinks = document.querySelectorAll('#file-list a');
    let currentFileUrl = ''; // Global variable to store the URL of the currently previewed file

    const previewable_extensions = {
        images: ['jpg', 'jpeg', 'png', 'gif', 'svg', 'bmp', 'webp'],
        text: ['txt', 'md', 'py', 'js', 'css', 'html', 'json', 'xml', 'sh', 'bat', 'log', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'odt', 'ods', 'odp', 'rtf', 'csv', 'mp3', 'wav', 'ogg', 'mp4', 'avi', 'mov', 'mkv', 'psd', 'crt', 'gz', 'zip', 'php', 'cpp', 'jar', 'key']
    };

    fileLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault(); // Always prevent default to open modal

            currentFileUrl = link.href; // Store the current file URL

            const url = new URL(link.href);
            const extension = url.pathname.split('.').pop().toLowerCase();

            const isImage = previewable_extensions.images.includes(extension);
            const isText = previewable_extensions.text.includes(extension);

            previewContent.innerHTML = ''; // Clear previous content
            const metadataContent = document.getElementById('metadata-content');
            metadataContent.innerHTML = '';
            modal.style.display = 'block';

            // Display preview if image or text
            if (isImage) {
                const img = document.createElement('img');
                img.src = link.href;
                previewContent.appendChild(img);
            } else if (isText) {
                fetch(link.href)
                    .then(response => response.text())
                    .then(text => {
                        const pre = document.createElement('pre');
                        pre.textContent = text;
                        previewContent.appendChild(pre);
                    })
                    .catch(err => {
                        console.error('Failed to fetch file content: ', err);
                        previewContent.textContent = 'Failed to load file content.';
                    });
            } else {
                // For other file types, show a message or just metadata
                previewContent.textContent = 'No visual preview available for this file type.';
            }

            // Always fetch and display metadata
            fetch(`/metadata?file=${url.pathname}`)
                .then(response => response.json())
                .then(data => {
                    const table = document.createElement('table');
                    const tbody = document.createElement('tbody');
                    for (const [key, value] of Object.entries(data)) {
                        const row = document.createElement('tr');
                        const keyCell = document.createElement('td');
                        keyCell.textContent = key;
                        const valueCell = document.createElement('td');
                        valueCell.textContent = value;
                        row.appendChild(keyCell);
                        row.appendChild(valueCell);
                        tbody.appendChild(row);
                    }
                    if (Object.keys(data).length > 0) {
                        const heading = document.createElement('h3');
                        heading.textContent = 'Metadata';
                        metadataContent.appendChild(heading);
                        table.appendChild(tbody);
                        metadataContent.appendChild(table);
                    } else {
                        metadataContent.textContent = 'No metadata found for this file.';
                    }
                })
                .catch(err => {
                    console.error('Failed to fetch metadata: ', err);
                    metadataContent.textContent = 'Failed to load metadata.';
                });
        });
    });

    closeBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    window.addEventListener('click', (e) => {
        if (e.target == modal) {
            modal.style.display = 'none';
        }
    });

    // Download button functionality
    const downloadBtn = document.getElementById('download-btn');
    downloadBtn.addEventListener('click', () => {
        if (currentFileUrl) {
            const a = document.createElement('a');
            a.href = currentFileUrl;
            a.download = currentFileUrl.split('/').pop(); // Suggest filename from URL
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        }
    });

    // Log Viewer
    const logToggleBtn = document.getElementById('log-toggle-btn');
    const logViewer = document.getElementById('log-viewer');
    const logContent = document.getElementById('log-content');
    let logInterval = null;

    const fetchLogs = () => {
        fetch('/logs')
            .then(response => response.text())
            .then(text => {
                logContent.textContent = text;
                logContent.scrollTop = logContent.scrollHeight;
            })
            .catch(err => {
                console.error('Failed to fetch logs:', err);
            });
    };

    logToggleBtn.addEventListener('click', () => {
        logViewer.classList.toggle('visible');
        if (logViewer.classList.contains('visible')) {
            fetchLogs();
            logInterval = setInterval(fetchLogs, 2000);
        } else {
            clearInterval(logInterval);
        }
    });
});

