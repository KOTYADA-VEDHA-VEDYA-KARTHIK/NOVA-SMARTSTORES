"""
NOVA SMARTOPS — Predictive Operations Backend Server
Built for NOVA CART Hackathon Prototype
Zero-dependency Python 3 HTTP + REST API Server
"""

import http.server
import socketserver
import json
import os
import urllib.parse
import math

PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# Ground Truth Mock Dataset for NOVA CART Partner Store #402
INVENTORY_DATA = [
    {"id": "SKU-101", "name": "Amul Taaza Milk 1L", "category": "Dairy & Eggs", "currentStock": 20, "history": [14, 12, 15, 13, 11, 14, 16, 13, 14, 15, 13, 12, 14, 15], "status": "ACTIVE"},
    {"id": "SKU-102", "name": "Britannia Whole Wheat Bread", "category": "Bakery", "currentStock": 18, "history": [7, 9, 8, 6, 8, 9, 7, 8, 9, 7, 8, 10, 8, 7], "status": "ACTIVE"},
    {"id": "SKU-103", "name": "India Gate Basmati Rice 5kg", "category": "Staples & Grains", "currentStock": 42, "history": [5, 4, 6, 5, 4, 5, 6, 4, 5, 5, 6, 4, 5, 5], "status": "ACTIVE"},
    {"id": "SKU-104", "name": "Farm Fresh Eggs (Pack of 12)", "category": "Dairy & Eggs", "currentStock": 8, "history": [8, 9, 7, 8, 9, 8, 10, 8, 9, 8, 9, 10, 9, 8], "status": "ACTIVE"},
    {"id": "SKU-105", "name": "Fresh Red Onion 1kg", "category": "Fresh Produce", "currentStock": 15, "history": [10, 11, 9, 12, 10, 11, 13, 10, 11, 12, 11, 10, 12, 11], "status": "ACTIVE"},
    {"id": "SKU-106", "name": "Hybrid Tomato 1kg", "category": "Fresh Produce", "currentStock": 12, "history": [8, 9, 8, 7, 9, 8, 9, 8, 9, 8, 9, 8, 9, 8], "status": "ACTIVE"},
    {"id": "SKU-107", "name": "Aashirvaad Shudh Chakki Atta 5kg", "category": "Staples & Grains", "currentStock": 35, "history": [4, 3, 5, 4, 3, 4, 5, 3, 4, 4, 5, 3, 4, 4], "status": "ACTIVE"},
    {"id": "SKU-108", "name": "Amul Masti Dahi 400g", "category": "Dairy & Eggs", "currentStock": 6, "history": [9, 10, 8, 11, 9, 10, 11, 9, 10, 11, 10, 9, 11, 10], "status": "ACTIVE"},
    {"id": "SKU-109", "name": "Robusta Banana (1 Dozen)", "category": "Fresh Produce", "currentStock": 9, "history": [6, 7, 6, 5, 7, 6, 7, 6, 7, 6, 7, 5, 7, 6], "status": "ACTIVE"},
    {"id": "SKU-110", "name": "Fortune Sunlite Sunflower Oil 1L", "category": "Staples & Grains", "currentStock": 25, "history": [3, 2, 3, 4, 3, 2, 3, 3, 2, 3, 4, 3, 2, 3], "status": "ACTIVE"},
    {"id": "SKU-111", "name": "Tata Salt Vaccum Evaporated 1kg", "category": "Staples & Grains", "currentStock": 50, "history": [4, 3, 4, 3, 4, 3, 4, 4, 3, 4, 3, 4, 3, 4], "status": "ACTIVE"},
    {"id": "SKU-112", "name": "Maggi 2-Minute Noodles (Pack of 4)", "category": "Packaged Foods", "currentStock": 14, "history": [9, 8, 10, 9, 11, 10, 12, 10, 11, 12, 11, 10, 12, 11], "status": "ACTIVE"}
]

ORDERS_DATA = [
    {"id": "ORD-1048", "store": "Fresh Mart (Indiranagar)", "distance": 6.8, "items": 9, "prepTime": 18, "storeLoad": "HIGH", "availablePartners": 1, "isPrioritized": False},
    {"id": "ORD-1050", "store": "Sharma Grocery (Koramangala)", "distance": 7.2, "items": 11, "prepTime": 20, "storeLoad": "HIGH", "availablePartners": 1, "isPrioritized": False},
    {"id": "ORD-1046", "store": "Metro Bazaar (HSR Layout)", "distance": 5.7, "items": 8, "prepTime": 15, "storeLoad": "HIGH", "availablePartners": 1, "isPrioritized": False},
    {"id": "ORD-1044", "store": "Daily Needs (Whitefield)", "distance": 4.5, "items": 6, "prepTime": 12, "storeLoad": "MEDIUM", "availablePartners": 2, "isPrioritized": False},
    {"id": "ORD-1047", "store": "Green Valley Organics", "distance": 3.9, "items": 5, "prepTime": 10, "storeLoad": "MEDIUM", "availablePartners": 2, "isPrioritized": False},
    {"id": "ORD-1051", "store": "Daily Needs (Jayanagar)", "distance": 3.1, "items": 4, "prepTime": 9, "storeLoad": "MEDIUM", "availablePartners": 3, "isPrioritized": False},
    {"id": "ORD-1042", "store": "ABC Supermarket (BTM)", "distance": 3.2, "items": 4, "prepTime": 8, "storeLoad": "LOW", "availablePartners": 3, "isPrioritized": False},
    {"id": "ORD-1043", "store": "Fresh Mart (MG Road)", "distance": 2.1, "items": 3, "prepTime": 6, "storeLoad": "LOW", "availablePartners": 4, "isPrioritized": False},
    {"id": "ORD-1045", "store": "QuickStop Express (Domlur)", "distance": 1.8, "items": 2, "prepTime": 5, "storeLoad": "LOW", "availablePartners": 5, "isPrioritized": False},
    {"id": "ORD-1049", "store": "ABC Grocery (Bellandur)", "distance": 2.5, "items": 3, "prepTime": 7, "storeLoad": "LOW", "availablePartners": 3, "isPrioritized": False}
]

def analyze_product_demand(p, forecast_days=3):
    sales = p["history"]
    avg_daily_demand = sum(sales) / len(sales)
    recent_3d_avg = sum(sales[-3:]) / 3
    trend_factor = recent_3d_avg / avg_daily_demand
    
    trend = "STABLE"
    if trend_factor > 1.06:
        trend = "RISING"
    elif trend_factor < 0.94:
        trend = "FALLING"

    predicted_demand = round(avg_daily_demand * trend_factor * forecast_days)
    safety_buffer = math.ceil(predicted_demand * 0.1)
    total_required = predicted_demand + safety_buffer

    if p["currentStock"] < predicted_demand:
        risk = "HIGH"
        risk_color = "red"
        action = "RESTOCK NOW"
    elif p["currentStock"] <= total_required:
        risk = "MEDIUM"
        risk_color = "amber"
        action = "RESTOCK SOON"
    else:
        risk = "LOW"
        risk_color = "green"
        action = "STOCK HEALTHY"

    recommended_restock = max(total_required - p["currentStock"], 0)

    return {
        **p,
        "avgDailySales": round(avg_daily_demand, 1),
        "trend": trend,
        "trendFactor": round(trend_factor, 2),
        "predictedDemand": predicted_demand,
        "safetyBuffer": safety_buffer,
        "totalRequired": total_required,
        "risk": risk,
        "riskColor": risk_color,
        "recommendedRestock": recommended_restock,
        "action": action
    }

def calculate_delivery_eta(order):
    is_p = order.get("isPrioritized", False)
    speed_min_per_km = 3.0
    sla_target = 30

    travel_time = round(order["distance"] * speed_min_per_km)
    workload_penalty = 12 if order["storeLoad"] == "HIGH" else (5 if order["storeLoad"] == "MEDIUM" else 0)
    item_penalty = round((order["items"] - 5) * 1.5) if order["items"] > 5 else 0
    partner_penalty = 6 if order["availablePartners"] <= 1 else 0

    prep_effective = max(5, order["prepTime"] - 6) if is_p else order["prepTime"]
    effective_workload = math.floor(workload_penalty * 0.4) if is_p else workload_penalty
    effective_partner = 1 if is_p else partner_penalty

    estimated_eta = prep_effective + travel_time + effective_workload + item_penalty + effective_partner

    if estimated_eta > sla_target + 5:
        risk = "HIGH"
        recs = [
            "Assign nearest dedicated delivery partner",
            "Prioritize queue in store dispatch station",
            "Proactively update customer ETA to prevent friction"
        ]
    elif estimated_eta >= sla_target - 2:
        risk = "MEDIUM"
        recs = [
            "Pre-reserve next incoming rider",
            "Monitor packaging progress closely"
        ]
    else:
        risk = "LOW"
        recs = ["Optimal operational flow — on target for SLA"]

    return {
        **order,
        "travelTime": travel_time,
        "workloadPenalty": workload_penalty,
        "itemPenalty": item_penalty,
        "partnerPenalty": partner_penalty,
        "prepEffective": prep_effective,
        "estimatedDeliveryTime": estimated_eta,
        "slaTarget": sla_target,
        "delayDelta": estimated_eta - sla_target,
        "risk": risk,
        "recommendations": recs
    }

class SmartOpsHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def send_json(self, data, status=200):
        response_bytes = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response_bytes)))
        self.end_headers()
        self.wfile.write(response_bytes)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/health":
            self.send_json({
                "status": "healthy",
                "service": "NOVA SMARTOPS API",
                "version": "1.0.0",
                "store": "NOVA CART Store #402"
            })
            return

        elif path == "/api/stats":
            self.send_json({
                "registeredUsers": 120000,
                "monthlyOrders": 38500,
                "cancellationRate": 11.0,
                "monthlyCancellations": 4235,
                "unavailabilityShare": 35.0,
                "delayShare": 27.0,
                "aov": 486,
                "repeatPurchase": 27.0,
                "targetRetention": 72.0
            })
            return

        elif path == "/api/inventory":
            analyzed = [analyze_product_demand(p) for p in INVENTORY_DATA]
            analyzed.sort(key=lambda x: (3 if x["risk"] == "HIGH" else (2 if x["risk"] == "MEDIUM" else 1)), reverse=True)
            self.send_json({"items": analyzed})
            return

        elif path == "/api/orders":
            computed = [calculate_delivery_eta(o) for o in ORDERS_DATA]
            computed.sort(key=lambda x: (3 if x["risk"] == "HIGH" else (2 if x["risk"] == "MEDIUM" else 1)), reverse=True)
            self.send_json({"orders": computed})
            return

        # Serve static files (index.html, etc.)
        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else b'{}'
        
        try:
            payload = json.loads(body.decode('utf-8'))
        except Exception:
            payload = {}

        if path == "/api/inventory/analyze":
            analyzed = [analyze_product_demand(p) for p in INVENTORY_DATA]
            analyzed.sort(key=lambda x: (3 if x["risk"] == "HIGH" else (2 if x["risk"] == "MEDIUM" else 1)), reverse=True)
            self.send_json({
                "success": True,
                "timestamp": "2026-10-02T12:00:00Z",
                "totalAnalyzed": len(analyzed),
                "highRisk": len([p for p in analyzed if p["risk"] == "HIGH"]),
                "mediumRisk": len([p for p in analyzed if p["risk"] == "MEDIUM"]),
                "items": analyzed
            })
            return

        elif path == "/api/inventory/restock":
            sku_id = payload.get("id")
            for p in INVENTORY_DATA:
                if p["id"] == sku_id:
                    p["status"] = "RESTOCK ORDERED"
                    p["currentStock"] += payload.get("qty", 15)
                    self.send_json({"success": True, "item": analyze_product_demand(p)})
                    return
            self.send_json({"error": "SKU not found"}, status=404)
            return

        elif path == "/api/inventory/delist":
            sku_id = payload.get("id")
            for p in INVENTORY_DATA:
                if p["id"] == sku_id:
                    p["status"] = "MARKED UNAVAILABLE"
                    self.send_json({"success": True, "item": analyze_product_demand(p)})
                    return
            self.send_json({"error": "SKU not found"}, status=404)
            return

        elif path == "/api/orders/prioritize":
            order_id = payload.get("id")
            for o in ORDERS_DATA:
                if o["id"] == order_id:
                    o["isPrioritized"] = True
                    updated = calculate_delivery_eta(o)
                    self.send_json({"success": True, "order": updated})
                    return
            self.send_json({"error": "Order not found"}, status=404)
            return

        elif path == "/api/impact/simulate":
            stockout_red = payload.get("stockoutReduction", 40)
            delay_red = payload.get("delayReduction", 30)

            monthly_orders = 38500
            current_cancellations = 4235
            stockout_cancellations = 1482
            delay_cancellations = 1143
            aov = 486

            prevented_stockout = round(stockout_cancellations * (stockout_red / 100))
            prevented_delay = round(delay_cancellations * (delay_red / 100))
            total_prevented = prevented_stockout + prevented_delay
            projected_cancellations = current_cancellations - total_prevented
            projected_rate = round((projected_cancellations / monthly_orders) * 100, 1)
            revenue_retained = total_prevented * aov

            self.send_json({
                "preventedCancellations": total_prevented,
                "projectedCancellationRate": projected_rate,
                "monthlyRevenueRetained": revenue_retained,
                "annualizedRevenueRetained": revenue_retained * 12,
                "supportTicketsReduced": round(total_prevented * 0.95)
            })
            return

        self.send_json({"error": "Endpoint not found"}, status=404)

if __name__ == "__main__":
    os.chdir(DIRECTORY)
    with socketserver.TCPServer(("", PORT), SmartOpsHandler) as httpd:
        print(f"============================================================")
        print(f"⚡ NOVA SMARTOPS BACKEND RUNNING ON http://localhost:{PORT}")
        print(f"⚡ Open http://localhost:{PORT} in your browser to view dashboard")
        print(f"============================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")
