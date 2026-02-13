// Virtual Christmas Tree Decorator
class TreeDecorator {
    constructor() {
        this.treeContainer = document.getElementById('treeContainer');
        this.ornamentZone = document.getElementById('ornamentZone');
        this.treeSvg = document.getElementById('treeSvg');
        this.ornaments = [];
        this.selectedOrnament = null;
        this.draggedElement = null;
        this.lightsInterval = null;
        this.garlandPath = null;
        
        this.settings = {
            treeSize: 1,
            treeColor: 'green',
            lightsEnabled: false,
            lightColor: 'multicolor',
            lightSpeed: 1,
            garlandEnabled: false,
            garlandStyle: 'tinsel'
        };
        
        this.init();
    }
    
    init() {
        this.setupDragAndDrop();
        this.setupControls();
        this.setupTreeInteractions();
    }
    
    setupDragAndDrop() {
        const ornamentItems = document.querySelectorAll('.ornament-item');
        
        ornamentItems.forEach(item => {
            item.addEventListener('dragstart', (e) => {
                this.draggedElement = e.target;
                e.dataTransfer.effectAllowed = 'copy';
                e.dataTransfer.setData('text/html', e.target.innerHTML);
            });
        });
        
        this.ornamentZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'copy';
        });
        
        this.ornamentZone.addEventListener('drop', (e) => {
            e.preventDefault();
            if (this.draggedElement) {
                const rect = this.ornamentZone.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                this.addOrnament(
                    this.draggedElement.dataset.type,
                    x,
                    y
                );
            }
        });
        
        // Click to add ornament
        ornamentItems.forEach(item => {
            item.addEventListener('click', () => {
                const rect = this.ornamentZone.getBoundingClientRect();
                const centerX = rect.width / 2;
                const centerY = rect.height / 2 + 50;
                this.addOrnament(
                    item.dataset.type,
                    centerX,
                    centerY
                );
            });
        });
    }
    
    addOrnament(type, x, y) {
        const ornament = document.createElement('div');
        ornament.className = 'ornament';
        ornament.dataset.type = type;
        
        // Get emoji based on type
        const emojis = {
            'ball-red': '🔴',
            'ball-blue': '🔵',
            'ball-gold': '🟡',
            'star': '⭐',
            'bell': '🔔',
            'gift': '🎁',
            'candy': '🍬',
            'snowflake': '❄️',
            'angel': '👼',
            'heart': '❤️',
            'light': '💡',
            'bow': '🎀'
        };
        
        ornament.textContent = emojis[type] || '🎄';
        ornament.style.left = x + 'px';
        ornament.style.top = y + 'px';
        
        // Make draggable
        this.makeDraggable(ornament);
        
        // Add click to select
        ornament.addEventListener('click', (e) => {
            e.stopPropagation();
            this.selectOrnament(ornament);
        });
        
        // Add delete on double click
        ornament.addEventListener('dblclick', () => {
            ornament.remove();
            this.ornaments = this.ornaments.filter(o => o !== ornament);
        });
        
        this.ornamentZone.appendChild(ornament);
        this.ornaments.push(ornament);
    }
    
    makeDraggable(element) {
        let isDragging = false;
        let currentX, currentY, initialX, initialY;
        
        element.addEventListener('mousedown', (e) => {
            if (e.target === element || element.contains(e.target)) {
                isDragging = true;
                element.classList.add('dragging');
                initialX = e.clientX - element.offsetLeft;
                initialY = e.clientY - element.offsetTop;
            }
        });
        
        document.addEventListener('mousemove', (e) => {
            if (isDragging) {
                e.preventDefault();
                currentX = e.clientX - initialX;
                currentY = e.clientY - initialY;
                
                const rect = this.ornamentZone.getBoundingClientRect();
                currentX = Math.max(0, Math.min(currentX, rect.width - 40));
                currentY = Math.max(0, Math.min(currentY, rect.height - 40));
                
                element.style.left = currentX + 'px';
                element.style.top = currentY + 'px';
            }
        });
        
        document.addEventListener('mouseup', () => {
            if (isDragging) {
                isDragging = false;
                element.classList.remove('dragging');
            }
        });
    }
    
    selectOrnament(ornament) {
        // Deselect previous
        if (this.selectedOrnament) {
            this.selectedOrnament.classList.remove('selected');
        }
        
        // Select new
        this.selectedOrnament = ornament;
        ornament.classList.add('selected');
        
        // Delete selected ornament with Delete key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Delete' && this.selectedOrnament) {
                this.selectedOrnament.remove();
                this.ornaments = this.ornaments.filter(o => o !== this.selectedOrnament);
                this.selectedOrnament = null;
            }
        }, { once: true });
    }
    
    setupControls() {
        // Tree size
        const treeSizeSlider = document.getElementById('treeSize');
        const treeSizeValue = document.getElementById('treeSizeValue');
        treeSizeSlider.addEventListener('input', (e) => {
            this.settings.treeSize = parseFloat(e.target.value);
            treeSizeValue.textContent = Math.round(this.settings.treeSize * 100) + '%';
            this.treeSvg.style.transform = `scale(${this.settings.treeSize})`;
            this.treeSvg.style.transformOrigin = 'center top';
        });
        
        // Tree color
        document.getElementById('treeColor').addEventListener('change', (e) => {
            this.settings.treeColor = e.target.value;
            this.updateTreeColor();
        });
        
        // Lights
        document.getElementById('enableLights').addEventListener('change', (e) => {
            this.settings.lightsEnabled = e.target.checked;
            if (e.target.checked) {
                this.startLights();
            } else {
                this.stopLights();
            }
        });
        
        document.getElementById('lightColor').addEventListener('change', (e) => {
            this.settings.lightColor = e.target.value;
            if (this.settings.lightsEnabled) {
                this.stopLights();
                this.startLights();
            }
        });
        
        const lightSpeedSlider = document.getElementById('lightSpeed');
        const lightSpeedValue = document.getElementById('lightSpeedValue');
        lightSpeedSlider.addEventListener('input', (e) => {
            this.settings.lightSpeed = parseFloat(e.target.value);
            lightSpeedValue.textContent = this.settings.lightSpeed.toFixed(1);
            if (this.settings.lightsEnabled) {
                this.stopLights();
                this.startLights();
            }
        });
        
        // Garland
        document.getElementById('enableGarland').addEventListener('change', (e) => {
            this.settings.garlandEnabled = e.target.checked;
            this.updateGarland();
        });
        
        document.getElementById('garlandStyle').addEventListener('change', (e) => {
            this.settings.garlandStyle = e.target.value;
            if (this.settings.garlandEnabled) {
                this.updateGarland();
            }
        });
        
        // Clear button
        document.getElementById('clearBtn').addEventListener('click', () => {
            if (confirm('Clear all ornaments?')) {
                this.ornaments.forEach(ornament => ornament.remove());
                this.ornaments = [];
                this.selectedOrnament = null;
            }
        });
        
        // Export button
        document.getElementById('exportBtn').addEventListener('click', () => {
            this.exportTree();
        });
        
        // Share button
        document.getElementById('shareBtn').addEventListener('click', () => {
            this.shareTree();
        });
    }
    
    setupTreeInteractions() {
        // Click outside to deselect
        this.ornamentZone.addEventListener('click', (e) => {
            if (e.target === this.ornamentZone) {
                if (this.selectedOrnament) {
                    this.selectedOrnament.classList.remove('selected');
                    this.selectedOrnament = null;
                }
            }
        });
    }
    
    updateTreeColor() {
        this.treeContainer.className = 'tree-container tree-' + this.settings.treeColor;
    }
    
    startLights() {
        this.stopLights();
        
        const lightOrnaments = this.ornaments.filter(o => o.dataset.type === 'light');
        if (lightOrnaments.length === 0) {
            // Add some default lights if none exist
            this.addDefaultLights();
        }
        
        const allLights = this.ornamentZone.querySelectorAll('.ornament[data-type="light"]');
        const speed = 1000 / this.settings.lightSpeed;
        
        this.lightsInterval = setInterval(() => {
            allLights.forEach((light, index) => {
                setTimeout(() => {
                    light.classList.toggle('light-twinkle');
                }, (index * speed) / allLights.length);
            });
        }, speed);
    }
    
    addDefaultLights() {
        const positions = [
            { x: 150, y: 250 },
            { x: 200, y: 280 },
            { x: 250, y: 250 },
            { x: 180, y: 320 },
            { x: 220, y: 320 },
            { x: 200, y: 360 }
        ];
        
        positions.forEach(pos => {
            this.addOrnament('light', pos.x, pos.y);
        });
    }
    
    stopLights() {
        if (this.lightsInterval) {
            clearInterval(this.lightsInterval);
            this.lightsInterval = null;
        }
        
        const allLights = this.ornamentZone.querySelectorAll('.ornament[data-type="light"]');
        allLights.forEach(light => {
            light.classList.remove('light-twinkle');
        });
    }
    
    updateGarland() {
        // Remove existing garland
        if (this.garlandPath) {
            this.garlandPath.remove();
        }
        
        if (!this.settings.garlandEnabled) {
            return;
        }
        
        // Create SVG path for garland
        const svgNS = 'http://www.w3.org/2000/svg';
        this.garlandPath = document.createElementNS(svgNS, 'path');
        
        // Create wavy garland path
        const pathData = this.createGarlandPath();
        this.garlandPath.setAttribute('d', pathData);
        this.garlandPath.setAttribute('class', `garland-line ${this.settings.garlandStyle}`);
        
        this.treeSvg.appendChild(this.garlandPath);
    }
    
    createGarlandPath() {
        // Create a wavy path around the tree
        const points = [];
        const centerX = 200;
        const baseY = 550;
        const topY = 200;
        
        for (let y = topY; y <= baseY; y += 20) {
            const width = 100 + (y - topY) * 0.3;
            const wave = Math.sin(y / 30) * 10;
            points.push(`${centerX - width / 2 + wave},${y}`);
        }
        
        return 'M ' + points.join(' L ') + ' Z';
    }
    
    exportTree() {
        // Create a canvas to export the tree
        const canvas = document.createElement('canvas');
        canvas.width = 1200;
        canvas.height = 1800;
        const ctx = canvas.getContext('2d');
        
        // Draw background
        ctx.fillStyle = '#1a1a2e';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Draw tree (simplified - in production use html2canvas)
        ctx.fillStyle = '#228B22';
        ctx.beginPath();
        ctx.moveTo(600, 200);
        ctx.lineTo(200, 1500);
        ctx.lineTo(1000, 1500);
        ctx.closePath();
        ctx.fill();
        
        // Draw ornaments (simplified)
        this.ornaments.forEach(ornament => {
            const rect = ornament.getBoundingClientRect();
            const zoneRect = this.ornamentZone.getBoundingClientRect();
            const x = (rect.left - zoneRect.left) * (canvas.width / zoneRect.width);
            const y = (rect.top - zoneRect.top) * (canvas.height / zoneRect.height);
            
            ctx.font = '60px Arial';
            ctx.fillText(ornament.textContent, x, y);
        });
        
        // Convert to image and download
        canvas.toBlob((blob) => {
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'christmas-tree.png';
            a.click();
            URL.revokeObjectURL(url);
        });
    }
    
    shareTree() {
        const ornamentCount = this.ornaments.length;
        const text = `Check out my decorated Christmas tree with ${ornamentCount} ornaments! 🎄✨`;
        
        if (navigator.share) {
            navigator.share({
                title: 'My Christmas Tree',
                text: text,
                url: window.location.href
            });
        } else {
            navigator.clipboard.writeText(text).then(() => {
                alert('Tree design description copied to clipboard!');
            });
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new TreeDecorator();
});







