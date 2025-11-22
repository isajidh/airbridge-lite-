function uploadFiles() {
    const input = document.getElementById('fileInput');
    const files = input.files;
    const progress = document.getElementById('progress');
    progress.innerHTML = '';
    // TODO: Implement AJAX upload logic
    for (let i = 0; i < files.length; i++) {
        progress.innerHTML += `<p>Uploading: ${files[i].name}</p>`;
    }
}
