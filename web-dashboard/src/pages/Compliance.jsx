import React from 'react';
import { ShieldCheck, Database, Lock } from 'lucide-react';

const Card = ({ children, className }) => <div className={`bg-white border rounded-xl shadow-sm ${className}`}>{children}</div>;
const CardHeader = ({ children }) => <div className="p-6 border-b">{children}</div>;
const CardTitle = ({ children }) => <h3 className="text-lg font-semibold flex items-center">{children}</h3>;
const CardContent = ({ children }) => <div className="p-6">{children}</div>;

export default function CompliancePage() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">Compliance & Data Privacy</h1>
      <Card>
          <CardHeader>
              <CardTitle><ShieldCheck className="mr-2 h-5 w-5 text-green-600"/>Privacy Framework</CardTitle>
          </CardHeader>
          <CardContent>
              <p className="text-gray-600">Our system is built with GDPR & CCPA principles in mind, ensuring data minimization and user control.</p>
          </CardContent>
      </Card>
      <Card>
          <CardHeader>
              <CardTitle><Database className="mr-2 h-5 w-5 text-blue-600"/>Data Retention</CardTitle>
          </CardHeader>
          <CardContent>
              <p className="text-gray-600">All detailed activity data is automatically deleted after 90 days. Aggregated, anonymized statistics are retained for trend analysis.</p>
          </CardContent>
      </Card>
      <Card>
          <CardHeader>
              <CardTitle><Lock className="mr-2 h-5 w-5 text-gray-600"/>Data Encryption</CardTitle>
          </CardHeader>
          <CardContent>
              <p className="text-gray-600">All data is encrypted both in transit (using TLS/SSL) and at rest (using AES-256) to ensure the highest level of security.</p>
          </CardContent>
      </Card>
    </div>
  )
}