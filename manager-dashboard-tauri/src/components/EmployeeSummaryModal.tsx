
import { X, Clock, TrendingUp, Target } from 'lucide-react';
import { Button } from './ui/Button';

interface TeamMember {
  userId: string;
  name: string;
  role: string;
  productiveHours?: number;
  unproductiveHours?: number;
  goalsCompleted?: number;
}

interface EmployeeSummaryModalProps {
  member: TeamMember | null;
  isOpen: boolean;
  onClose: () => void;
}

export default function EmployeeSummaryModal({ member, isOpen, onClose }: EmployeeSummaryModalProps) {
  if (!isOpen || !member) return null;

  const totalHours = (member.productiveHours || 0) + (member.unproductiveHours || 0);
  const productivityRate = totalHours > 0 ? ((member.productiveHours || 0) / totalHours * 100).toFixed(1) : '0';

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl p-6 w-full max-w-md mx-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-gray-800">{member.name}</h2>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>
        
        <div className="space-y-4">
          <div>
            <p className="text-sm text-gray-500">Role</p>
            <p className="font-medium">{member.role}</p>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-green-50 p-3 rounded-lg">
              <div className="flex items-center text-green-600">
                <TrendingUp className="h-4 w-4 mr-1" />
                <span className="text-sm font-medium">Productive</span>
              </div>
              <p className="text-lg font-bold text-green-700">{member.productiveHours || 0}h</p>
            </div>
            
            <div className="bg-orange-50 p-3 rounded-lg">
              <div className="flex items-center text-orange-600">
                <Clock className="h-4 w-4 mr-1" />
                <span className="text-sm font-medium">Total</span>
              </div>
              <p className="text-lg font-bold text-orange-700">{totalHours}h</p>
            </div>
          </div>
          
          <div className="bg-blue-50 p-3 rounded-lg">
            <div className="flex items-center text-blue-600">
              <Target className="h-4 w-4 mr-1" />
              <span className="text-sm font-medium">Productivity Rate</span>
            </div>
            <p className="text-lg font-bold text-blue-700">{productivityRate}%</p>
          </div>
          
          <div className="bg-purple-50 p-3 rounded-lg">
            <div className="flex items-center text-purple-600">
              <Target className="h-4 w-4 mr-1" />
              <span className="text-sm font-medium">Goals Completed</span>
            </div>
            <p className="text-lg font-bold text-purple-700">{member.goalsCompleted || 0}</p>
          </div>
        </div>
        
        <div className="mt-6 flex justify-end">
          <Button onClick={onClose}>Close</Button>
        </div>
      </div>
    </div>
  );
}