import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Badge } from '../components/ui/Badge';
import { Users, Crown, Copy, UserPlus, TrendingUp, TrendingDown, Plus } from 'lucide-react';
import EmployeeSummaryModal from '../components/EmployeeSummaryModal';

// Updated to use the correct backend URL
const API_URL = "https://productivityflow-backend-v3.onrender.com";

export default function TeamManagementPage() {
  const [teams, setTeams] = useState([]);
  const [selectedTeam, setSelectedTeam] = useState(null);
  const [teamMembers, setTeamMembers] = useState([]);
  const [newTeamName, setNewTeamName] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [selectedMember, setSelectedMember] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => { loadTeams(); }, []);
  useEffect(() => { if (selectedTeam) loadTeamMembers(selectedTeam.id); }, [selectedTeam]);

  // Save selected team to localStorage
  useEffect(() => {
    if (selectedTeam) {
      localStorage.setItem('selectedTeamId', selectedTeam.id);
    }
  }, [selectedTeam]);

  const loadTeams = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/teams`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log("Teams API response:", data);
      
      // Handle both error responses and success responses
      if (data.error) {
        console.error("API error:", data.error);
        setTeams([]);
        return;
      }
      
      const teams = data.teams || [];
      setTeams(teams);
      
      // Try to restore previously selected team
      const savedTeamId = localStorage.getItem('selectedTeamId');
      if (savedTeamId && teams.length > 0) {
        const savedTeam = teams.find(team => team.id === savedTeamId);
        if (savedTeam) {
          setSelectedTeam(savedTeam);
        } else {
          // If saved team not found, select first team
          setSelectedTeam(teams[0]);
        }
      } else if (teams.length > 0 && !selectedTeam) {
        // If no saved team and no current selection, select first team
        setSelectedTeam(teams[0]);
      }
    } catch (error) {
      console.error("Failed to load teams:", error);
      setTeams([]); // Set empty array to prevent crashes
    } finally {
      setIsLoading(false);
    }
  };

  const loadTeamMembers = async (teamId) => {
    try {
      const response = await fetch(`${API_URL}/api/teams/${teamId}/members`);
      const data = await response.json();
      setTeamMembers(data.members);
    } catch (error) {
      console.error("Failed to load team members:", error);
      setTeamMembers([]);
    }
  };

  const handleCreateTeam = async () => {
    if (!newTeamName.trim()) return;
    try {
      const response = await fetch(`${API_URL}/api/teams`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            name: newTeamName,
            user_name: 'Manager' // Default user name for team creator
          })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      if (data.error) {
        throw new Error(data.error);
      }
      
      const newTeam = data.team ? data : data; // Handle different response formats
      setTeams(prevTeams => [...prevTeams, newTeam]);
      setSelectedTeam(newTeam); // This will automatically save to localStorage
      setNewTeamName("");
      
      // Show success message
      console.log("Team created successfully:", newTeam);
    } catch (error) {
      console.error("Failed to create team:", error);
      alert(`Failed to create team: ${error.message}`);
    }
  };

  const handleTeamSelect = (team) => {
    setSelectedTeam(team);
    // localStorage save happens automatically via useEffect
  };

  const handleMemberClick = (member) => {
    setSelectedMember(member);
    setIsModalOpen(true);
  };

  const copyTeamCode = (code) => {
    navigator.clipboard.writeText(code).then(() => alert("Team code copied!"));
  };

  return (
    <>
      <div className="space-y-6">
        {/* ... Rest of the JSX remains the same ... */}
        <h1 className="text-3xl font-bold tracking-tight">Team Management</h1>
        <Card>
            <CardHeader><CardTitle>Create a New Team</CardTitle></CardHeader>
            <CardContent>
                <div className="flex items-center space-x-2 max-w-md">
                    <Input value={newTeamName} onChange={(e) => setNewTeamName(e.target.value)} placeholder="E.g., Q3 Engineering Squad" />
                    <Button onClick={handleCreateTeam}><Plus className="h-4 w-4 mr-2" />Create Team</Button>
                </div>
            </CardContent>
        </Card>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="md:col-span-1">
            <Card>
              <CardHeader><CardTitle className="flex items-center"><Users className="mr-2 h-5 w-5"/>My Teams</CardTitle></CardHeader>
              <CardContent className="space-y-2">
                {teams.map(team => (
                  <button key={team.id} onClick={() => handleTeamSelect(team)} className={`w-full text-left p-3 rounded-lg border transition-colors ${selectedTeam?.id === team.id ? 'bg-indigo-100 border-indigo-300' : 'hover:bg-gray-100'}`}>
                    <div className="flex justify-between items-center"><span className="font-semibold text-gray-800">{team.name}</span><Badge>Active</Badge></div>
                    <p className="text-sm text-gray-500">{team.memberCount} members</p>
                  </button>
                ))}
              </CardContent>
            </Card>
          </div>
          <div className="md:col-span-3">
            {selectedTeam ? (
              <Card>
                <CardHeader><CardTitle className="flex items-center"><Crown className="mr-2 h-6 w-6 text-yellow-500"/>{selectedTeam.name} Details</CardTitle></CardHeader>
                <CardContent className="space-y-6">
                    <div>
                      <label className="text-sm font-medium text-gray-600">Team Join Code</label>
                      <div className="mt-2 flex items-center justify-between p-4 bg-gray-100 rounded-lg">
                        <span className="text-2xl font-mono tracking-widest text-indigo-600">{selectedTeam.code}</span>
                        <Button variant="ghost" size="sm" onClick={() => copyTeamCode(selectedTeam.code)}><Copy className="h-4 w-4"/></Button>
                      </div>
                    </div>
                    <div>
                    <div className="flex justify-between items-center mb-4"><h3 className="text-lg font-semibold">Team Members</h3><Button variant="outline"><UserPlus className="h-4 w-4 mr-2"/>Invite</Button></div>
                    <div className="space-y-3">
                      {teamMembers.map(member => (
                        <div key={member.userId} onClick={() => handleMemberClick(member)} className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 cursor-pointer">
                          <div className="flex items-center space-x-3">
                            <div className="w-9 h-9 bg-gray-200 rounded-full flex items-center justify-center"><span className="text-sm font-medium text-gray-600">{member.name.substring(0, 2).toUpperCase()}</span></div>
                            <div><p className="font-semibold text-gray-800">{member.name}</p><p className="text-sm text-gray-500">{member.role}</p></div>
                          </div>
                          <div className="flex items-center space-x-4">
                            <div className="flex items-center text-sm text-green-600 font-medium"><TrendingUp className="h-4 w-4 mr-1"/>{member.productiveHours || 0}h</div>
                            <div className="flex items-center text-sm text-orange-600 font-medium"><TrendingDown className="h-4 w-4 mr-1"/>{member.unproductiveHours || 0}h</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ) : <p>Create a team to get started.</p>}
          </div>
        </div>
      </div>
      {isModalOpen && <EmployeeSummaryModal member={selectedMember} isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />}
    </>
  );
}