import { useState, useEffect } from 'react';
import type { RefObject } from 'react';

export function useResizeObserver(ref: RefObject<HTMLElement | null>) {
    const [dimensions, setDimensions] = useState({ width: 0, height: 0 });

    useEffect(() => {
        if (!ref.current) return;

        const observer = new ResizeObserver((entries) => {
            if (!entries || entries.length === 0) return;
            const { width, height } = entries[0].contentRect;
            setDimensions({ width, height });
        });

        observer.observe(ref.current);

        return () => observer.disconnect();
    }, [ref]);

    return dimensions;
}
