document.addEventListener('DOMContentLoaded', function() {
    if (window.innerWidth < 768) {
        return; // Don't run on mobile devices
    }

    const MAX_LEAVES = 50;
    const leaves = [];
    let currentLeafIndex = 0;

    const leafContainer = document.createElement('div');
    leafContainer.setAttribute('id', 'leaf-container');
    document.body.appendChild(leafContainer);

    // --- Object Pooling: Create leaves upfront ---
    for (let i = 0; i < MAX_LEAVES; i++) {
        const leaf = document.createElement('span');
        leaf.className = 'leaf';
        leaf.style.display = 'none'; // Initially hidden
        leafContainer.appendChild(leaf);
        leaves.push(leaf);
    }

    const throttledCreateLeaf = throttle(triggerLeaf, 16); // Throttle to ~60fps

    document.addEventListener('mousemove', function(e) {
        throttledCreateLeaf(e.pageX, e.pageY);
    });

    function triggerLeaf(x, y) {
        const leaf = leaves[currentLeafIndex];
        
        // Move to the next leaf in the pool
        currentLeafIndex = (currentLeafIndex + 1) % MAX_LEAVES;

        // Reset any previous animation
        leaf.style.animation = 'none';
        leaf.offsetHeight; /* Trigger reflow */
        leaf.style.animation = '';

        // Position the leaf at the cursor
        leaf.style.left = x + 'px';
        leaf.style.top = y + 'px';
        leaf.style.display = 'block';

        // Add randomness for a natural effect
        const size = Math.random() * 20 + 10; // 10px to 30px
        const rotation = Math.random() * 360;
        const animationDuration = Math.random() * 1.5 + 1; // 1s to 2.5s

        leaf.style.width = size + 'px';
        leaf.style.height = size / 2 + 'px';
        leaf.style.setProperty('--rotation-end', rotation + 'deg');
        
        // Apply the fall animation
        leaf.style.animation = `fall ${animationDuration}s linear forwards`;

        // Hide the leaf after animation, making it available for reuse
        setTimeout(() => {
            leaf.style.display = 'none';
        }, animationDuration * 1000);
    }

    // --- Throttle utility to limit function calls ---
    function throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
});
