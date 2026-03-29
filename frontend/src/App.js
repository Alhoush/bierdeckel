import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Home from './customer/pages/Home';
import Menu from './customer/pages/Menu';
import Cart from './customer/pages/Cart';
import OrderHistory from './customer/pages/OrderHistory';
import Payment from './customer/pages/Payment';
import DrinkTogether from './customer/pages/DrinkTogether';
import Game from './customer/pages/Game';
import Profile from './customer/pages/Profile';
import History from './customer/pages/History';
import Leaderboard from './customer/pages/Leaderboard';
import Navbar from './customer/components/Navbar';
import Login from './dashboard/pages/Login';
import Dashboard from './dashboard/pages/Dashboard';
import MenuManager from './dashboard/pages/MenuManager';
import TableManager from './dashboard/pages/TableManager';
import StaffManager from './dashboard/pages/StaffManager';

function App() {
    return (
        <BrowserRouter>
            <Routes>
                {/* Kunden-App */}
                <Route path="/r/:restaurantId/bd/:bierdeckelId" element={<Home />} />
                <Route path="/menu" element={<><Menu /><Navbar /></>} />
                <Route path="/cart" element={<><Cart /><Navbar /></>} />
                <Route path="/orders" element={<><OrderHistory /><Navbar /></>} />
                <Route path="/payment" element={<><Payment /><Navbar /></>} />
                <Route path="/drink" element={<><DrinkTogether /><Navbar /></>} />
                <Route path="/game" element={<><Game /><Navbar /></>} />
                <Route path="/profile" element={<><Profile /><Navbar /></>} />
                <Route path="/history" element={<><History /><Navbar /></>} />
                <Route path="/leaderboard" element={<><Leaderboard /><Navbar /></>} />

                {/* Service-Dashboard */}
                <Route path="/login" element={<Login />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/dashboard/menu" element={<MenuManager />} />
                <Route path="/dashboard/tables" element={<TableManager />} />
                <Route path="/dashboard/staff" element={<StaffManager />} />
            </Routes>
        </BrowserRouter>
    );
}

export default App;