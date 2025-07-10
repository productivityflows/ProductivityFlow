import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card';
import { Button } from './ui/Button';
import { X, Loader2, BrainCircuit, TrendingUp, TrendingDown, Clock } from 'lucide-react';

const API_URL = "/api";

export default function EmployeeSummaryModal({ member, isOpen, onClose }) {
  const [summaryData, setSummaryData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (isOpen && member) {
      const fetchSummary = async () => {
        setIsLoading(true);
        try {
          const response = await fetch(`${API_URL}/employees/${member.userId}/summary`);
          const data = await response.json();
          setSummaryData(data);
        } catch (error) {
          setSummaryData({ error: "Could not load summary data." });
        } finally {
          setIsLoading(false);
        }
      };
      fetchSummary();
    }
  }, [isOpen, member]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-2xl bg-white rounded-xl shadow-2xl">
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle>Daily Report: {member.name}</CardTitle>
            <Button variant="ghost" size="sm" onClick={onClose}><X className="h-5 w-5"/></Button>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex justify-center items-center h-48"><Loader2 className="h-8 w-8 animate-spin text-indigo-600" /></div>
          ) : summaryData.error ? (
            <p className="text-red-500">{summaryData.error}</p>
          ) : (
            <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="text-center p-4 bg-gray-50 rounded-lg"><p className="text-sm font-medium text-gray-500">Productivity Score</p><p className="text-5xl font-bold text-green-600">{summaryData.productivityScore}%</p></div>
                    <div className="p-4 bg-gray-50 rounded-lg space-y-2">
                        <div className="flex justify-between items-center text-sm"><span className="flex items-center text-green-700"><TrendingUp className="h-4 w-4 mr-1.5"/>Productive</span><span className="font-semibold">{summaryData.productiveHours.toFixed(1)} hrs</span></div>
                        <div className="flex justify-between items-center text-sm"><span className="flex items-center text-orange-700"><TrendingDown className="h-4 w-4 mr-1.5"/>Unproductive</span><span className="font-semibold">{summaryData.unproductiveHours.toFixed(1)} hrs</span></div>
                        <div className="flex justify-between items-center text-sm"><span className="flex items-center text-gray-600"><Clock className="h-4 w-4 mr-1.5"/>Idle</span><span className="font-semibold">{summaryData.idleHours.toFixed(1)} hrs</span></div>
                    </div>
                </div>
                <div className="flex items-start space-x-4 p-4 bg-indigo-50 border border-indigo-200 rounded-lg">
                    <BrainCircuit className="h-8 w-8 text-indigo-600 flex-shrink-0 mt-1"/>
                    <div>
                        <h4 className="font-semibold text-gray-800">AI-Generated Summary</h4>
                        <p className="text-gray-600 text-sm" dangerouslySetInnerHTML={{ __html: summaryData.aiSummary }}></p>
                    </div>
                </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}