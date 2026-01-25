/**
 * Geometry Utility Module
 * Pure functions for 2D intersection and distance calculations.
 */

export class Geometry {
    /**
     * Checks if a line segment (p1-p2) intersects with a rectangle (rx, ry, w, h).
     * Uses AABB check first for performance.
     */
    static lineIntersectsRect(x1, y1, x2, y2, rx, ry, rw, rh) {
        // Optimization: AABB check first (Axis-Aligned Bounding Box)
        const minX = Math.min(x1, x2);
        const maxX = Math.max(x1, x2);
        const minY = Math.min(y1, y2);
        const maxY = Math.max(y1, y2);
        
        // If the line's bounding box doesn't touch the rect, no intersection possible
        if (maxX < rx || minX > rx + rw || maxY < ry || minY > ry + rh) {
            return false;
        }

        // Check intersection with any of the 4 sides
        const left = Geometry.lineIntersectsLine(x1, y1, x2, y2, rx, ry, rx, ry + rh);
        if (left) return true;
        
        const right = Geometry.lineIntersectsLine(x1, y1, x2, y2, rx + rw, ry, rx + rw, ry + rh);
        if (right) return true;
        
        const top = Geometry.lineIntersectsLine(x1, y1, x2, y2, rx, ry, rx + rw, ry);
        if (top) return true;
        
        const bottom = Geometry.lineIntersectsLine(x1, y1, x2, y2, rx, ry + rh, rx + rw, ry + rh);
        return bottom;
    }

    /**
     * Standard line-line intersection algorithm (denominator check).
     */
    static lineIntersectsLine(x1, y1, x2, y2, x3, y3, x4, y4) {
        const den = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1);
        
        // Parallel lines
        if (den === 0) return false;
        
        const uA = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / den;
        const uB = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / den;
        
        return (uA >= 0 && uA <= 1 && uB >= 0 && uB <= 1);
    }
    
    static distanceSq(x1, y1, x2, y2) {
        const dx = x1 - x2;
        const dy = y1 - y2;
        return dx * dx + dy * dy;
    }
}
