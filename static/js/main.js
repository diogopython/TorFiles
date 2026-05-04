/**
 * TorFiles - Main JavaScript
 * Funcionalidades que funcionam sem JavaScript tambem (progressive enhancement)
 */

(function() {
    'use strict';

    // ==========================================================================
    // Mobile Navigation Toggle
    // ==========================================================================
    
    var navbarToggle = document.getElementById('navbarToggle');
    var navbarMenu = document.querySelector('.navbar-menu');
    
    if (navbarToggle && navbarMenu) {
        navbarToggle.addEventListener('click', function() {
            navbarMenu.classList.toggle('active');
        });
        
        // Fechar ao clicar em um link
        var navLinks = navbarMenu.querySelectorAll('a');
        navLinks.forEach(function(link) {
            link.addEventListener('click', function() {
                navbarMenu.classList.remove('active');
            });
        });
    }

    // ==========================================================================
    // Auto-dismiss Flash Messages
    // ==========================================================================
    
    var flashMessages = document.querySelectorAll('.flash');
    flashMessages.forEach(function(flash) {
        setTimeout(function() {
            flash.style.opacity = '0';
            flash.style.transition = 'opacity 0.3s';
            setTimeout(function() {
                flash.remove();
            }, 300);
        }, 5000);
    });

    // ==========================================================================
    // Code Input Formatting
    // ==========================================================================
    
    var codeInput = document.querySelector('.code-input');
    if (codeInput) {
        codeInput.addEventListener('input', function() {
            this.value = this.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
        });
    }

    // ==========================================================================
    // Drag and Drop File Upload
    // ==========================================================================
    
    var fileInputWrapper = document.querySelector('.file-input-wrapper');
    var fileDisplay = document.getElementById('fileDisplay');
    
    if (fileInputWrapper && fileDisplay) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(function(eventName) {
            fileInputWrapper.addEventListener(eventName, function(e) {
                e.preventDefault();
                e.stopPropagation();
            });
        });
        
        ['dragenter', 'dragover'].forEach(function(eventName) {
            fileInputWrapper.addEventListener(eventName, function() {
                fileDisplay.classList.add('file-selected');
            });
        });
        
        ['dragleave', 'drop'].forEach(function(eventName) {
            fileInputWrapper.addEventListener(eventName, function() {
                fileDisplay.classList.remove('file-selected');
            });
        });
        
        fileInputWrapper.addEventListener('drop', function(e) {
            var files = e.dataTransfer.files;
            if (files.length > 0) {
                var fileInput = fileInputWrapper.querySelector('input[type="file"]');
                fileInput.files = files;
                
                // Trigger change event
                var event = new Event('change', { bubbles: true });
                fileInput.dispatchEvent(event);
            }
        });
    }

    // ==========================================================================
    // Copy to Clipboard with Feedback
    // ==========================================================================
    
    window.copyCode = function(code) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(code).then(function() {
                showCopyFeedback(event.currentTarget);
            }).catch(function() {
                fallbackCopy(code);
            });
        } else {
            fallbackCopy(code);
        }
    };
    
    function fallbackCopy(text) {
        var textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        
        try {
            document.execCommand('copy');
            showCopyFeedback(event.currentTarget);
        } catch (err) {
            console.error('Falha ao copiar');
        }
        
        document.body.removeChild(textarea);
    }
    
    function showCopyFeedback(button) {
        if (!button) return;
        
        var originalHTML = button.innerHTML;
        button.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>';
        button.style.color = 'var(--color-success)';
        
        setTimeout(function() {
            button.innerHTML = originalHTML;
            button.style.color = '';
        }, 1500);
    }

    // ==========================================================================
    // Form Validation Feedback
    // ==========================================================================
    
    var forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        var inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
        
        inputs.forEach(function(input) {
            input.addEventListener('invalid', function() {
                this.classList.add('invalid');
            });
            
            input.addEventListener('input', function() {
                if (this.validity.valid) {
                    this.classList.remove('invalid');
                }
            });
        });
    });

    // ==========================================================================
    // Confirm Delete Actions
    // ==========================================================================
    
    // Already handled inline with onsubmit, but we can enhance it
    var deleteButtons = document.querySelectorAll('.btn-danger[type="submit"]');
    deleteButtons.forEach(function(btn) {
        var form = btn.closest('form');
        if (form && !form.hasAttribute('onsubmit')) {
            form.addEventListener('submit', function(e) {
                if (!confirm('Tem certeza que deseja continuar?')) {
                    e.preventDefault();
                }
            });
        }
    });

    // ==========================================================================
    // Hash Verification Helper
    // ==========================================================================
    
    var hashValue = document.querySelector('.hash-value');
    if (hashValue) {
        hashValue.style.cursor = 'pointer';
        hashValue.title = 'Clique para copiar';
        
        hashValue.addEventListener('click', function() {
            var hash = this.textContent.trim();
            if (navigator.clipboard) {
                navigator.clipboard.writeText(hash).then(function() {
                    hashValue.style.background = 'var(--color-success-light)';
                    setTimeout(function() {
                        hashValue.style.background = '';
                    }, 1000);
                });
            }
        });
    }

    // ==========================================================================
    // Auto-refresh for Dashboard (optional)
    // ==========================================================================
    
    // Uncomment to enable auto-refresh every 60 seconds on dashboard
    // if (window.location.pathname === '/dashboard') {
    //     setTimeout(function() {
    //         window.location.reload();
    //     }, 60000);
    // }

})();
