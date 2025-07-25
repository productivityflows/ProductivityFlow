import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { CreditCard, AlertCircle, CheckCircle, Loader2 } from 'lucide-react';

// Correct API URL for all requests
const API_URL = "https://productivityflow-backend-v3.onrender.com";

interface SubscriptionStatus {
  status: string;
  current_period_end?: string;
  cancel_at_period_end?: boolean;
  total_amount?: number;
  employee_count?: number;
  price_per_employee?: number;
}

export default function BillingPage() {
  const [subscriptionData, setSubscriptionData] = useState<SubscriptionStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchSubscriptionData();
  }, []);

  const fetchSubscriptionData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/subscription/status`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const data: SubscriptionStatus = await response.json();
        setSubscriptionData(data);
      } else {
        setError('Failed to fetch subscription data');
      }
    } catch (err) {
      setError('Network error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdatePayment = async () => {
    try {
      const response = await fetch(`${API_URL}/api/subscription/update-payment`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const { checkout_url } = await response.json();
        window.open(checkout_url, '_blank');
      } else {
        setError('Failed to update payment method');
      }
    } catch (err) {
      setError('Failed to update payment method');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-600 bg-green-100';
      case 'trial': return 'text-blue-600 bg-blue-100';
      case 'past_due': return 'text-yellow-600 bg-yellow-100';
      case 'expired': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <CheckCircle className="w-5 h-5" />;
      case 'trial': return <Loader2 className="w-5 h-5" />; // Changed from Clock to Loader2 for trial
      case 'past_due': 
      case 'expired': return <AlertCircle className="w-5 h-5" />; // Changed from AlertTriangle to AlertCircle
      default: return <Loader2 className="w-5 h-5" />; // Default for unknown
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active': return 'Active Subscription';
      case 'trial': return 'Free Trial';
      case 'past_due': return 'Payment Required';
      case 'expired': return 'Subscription Expired';
      default: return 'Unknown Status';
    }
  };

  if (loading) {
    return (
      <div className="p-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="h-48 bg-gray-200 rounded"></div>
            <div className="h-48 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
            <p className="text-red-800">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Billing & Subscription</h1>
        <p className="text-gray-600">Manage your ProductivityFlow subscription and billing details</p>
      </div>

      {subscriptionData && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Subscription Status Card */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Subscription Status</CardTitle>
                <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(subscriptionData.status)}`}>
                  {getStatusIcon(subscriptionData.status)}
                  {getStatusText(subscriptionData.status)}
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {subscriptionData.status === 'trial' && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <div className="flex items-center">
                      <Loader2 className="w-5 h-5 text-blue-600 mr-2" />
                      <div>
                        <p className="text-blue-800 font-medium">Free Trial Active</p>
                        <p className="text-blue-600 text-sm">
                          Your free trial is active.
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {(subscriptionData.status === 'past_due' || subscriptionData.status === 'expired') && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <div className="flex items-center">
                      <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
                      <div>
                        <p className="text-red-800 font-medium">Action Required</p>
                        <p className="text-red-600 text-sm">
                          {subscriptionData.status === 'past_due' 
                            ? 'Your payment is past due. Update your payment method to avoid service interruption.'
                            : 'Your subscription has expired. Your team\'s access has been suspended.'
                          }
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-500">Current Period End</p>
                    <p className="font-medium text-gray-900">
                      {subscriptionData.current_period_end ? new Date(subscriptionData.current_period_end).toLocaleDateString() : 'N/A'}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Total Amount</p>
                    <p className="font-medium text-gray-900">
                      ${subscriptionData.total_amount?.toFixed(2) || '0.00'}/month
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Employee Count & Billing Card */}
          <Card>
            <CardHeader>
              <div className="flex items-center">
                <CreditCard className="w-6 h-6 text-indigo-600 mr-2" />
                <CardTitle>Employee Billing</CardTitle>
              </div>
            </CardHeader>
            <CardContent>

              <div className="space-y-4">
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm text-gray-500">Active Employees</span>
                    <span className="text-2xl font-bold text-gray-900">{subscriptionData.employee_count || 0}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-500">Price per Employee</span>
                    <span className="text-lg font-semibold text-gray-900">${subscriptionData.price_per_employee || 0}/month</span>
                  </div>
                </div>

                <div className="border-t pt-4">
                  <div className="flex justify-between items-center">
                    <span className="text-base font-medium text-gray-900">Monthly Total</span>
                    <span className="text-xl font-bold text-indigo-600">${subscriptionData.total_amount?.toFixed(2) || '0.00'}</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Payment Management Card */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <div className="flex items-center">
                <CreditCard className="w-6 h-6 text-indigo-600 mr-2" />
                <CardTitle>Payment Management</CardTitle>
              </div>
            </CardHeader>
            <CardContent>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Button
                  onClick={handleUpdatePayment}
                  className="flex items-center justify-center gap-2 bg-indigo-600 text-white px-4 py-3 rounded-lg hover:bg-indigo-700 transition-colors"
                >
                  <CreditCard className="w-5 h-5" />
                  Update Payment Method
                </Button>

                <Button
                  onClick={() => window.open(`${API_URL}/api/subscription/customer-portal`, '_blank')}
                  className="flex items-center justify-center gap-2 bg-gray-100 text-gray-700 px-4 py-3 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  <CreditCard className="w-5 h-5" />
                  Manage Subscription
                </Button>
              </div>

              <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                <h3 className="font-medium text-blue-900 mb-2">Important Information</h3>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li>• Your subscription automatically scales with your team size</li>
                  <li>• You're only charged for active team members</li>
                  <li>• If payment fails, team access will be suspended after 7 days</li>
                  <li>• All data is securely retained during payment issues</li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}