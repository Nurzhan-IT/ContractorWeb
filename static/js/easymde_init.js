document.addEventListener('DOMContentLoaded', function () {
    var el = document.getElementById('id_content');
    if (el) {
        new EasyMDE({
            element: el,
            spellChecker: false,
            toolbar: [
                'bold', 'italic', 'heading', '|',
                'quote', 'unordered-list', 'ordered-list', '|',
                'link', 'image', '|',
                'preview', 'side-by-side', 'fullscreen',
            ],
        });
    }
});
