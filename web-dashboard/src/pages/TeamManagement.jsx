import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Badge } from '../components/ui/Badge';
import { Users, Crown, Copy, UserPlus, TrendingUp, TrendingDown, Plus } from 'lucide-react';
import EmployeeSummaryModal from '../components/EmployeeSummaryModal';

const API_URL = "http://productivityflow-env.eba-ubkzaksh.us-east-2.elasticbeanstalk.com/";

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

  const loadTeams = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_URL}/teams`);
      const data = await response.json();
      setTeams(data.teams);
      if (data.teams.length > 0 && !selectedTeam) {
        setSelectedTeam(data.teams[0]);
      }
    } catch (error) {
      console.error("Failed to load teams:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadTeamMembers = async (teamId) => {
    const response = await fetch(`${API_URL}/teams/${teamId}/members`);
    const data = await response.json();
    setTeamMembers(data.members);
  };

  const handleCreateTeam = async () => {
    if (!newTeamName.trim()) return;
    const response = await fetch(`${API_URL}/teams`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newTeamName })
    });
    const newTeam = await response.json();

    // --- THIS IS THE FIX ---
    // Add the new team to our existing list and select it immediately.
    setTeams(prevTeams => [...prevTeams, newTeam]);
    setSelectedTeam(newTeam);
    // --- END OF FIX ---

    setNewTeamName("");
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
                  <button key={team.id} onClick={() => setSelectedTeam(team)} className={`w-full text-left p-3 rounded-lg border transition-colors ${selectedTeam?.id === team.id ? 'bg-indigo-100 border-indigo-300' : 'hover:bg-gray-100'}`}>
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