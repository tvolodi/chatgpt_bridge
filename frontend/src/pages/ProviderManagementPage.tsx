import React, { useState, useEffect } from 'react';
import { useProvidersStore } from '../stores/providersStore';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Plus, Edit, Trash2, CheckCircle, Settings } from 'lucide-react';

export const ProviderManagementPage: React.FC = () => {
  const {
    providers,
    providerConfigs,
    loadProviders,
    createProvider,
    updateProvider,
    deleteProvider,
    saveProviderConfig,
    validateProviderConfig,
    isLoading,
    error
  } = useProvidersStore();

  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [editingProvider, setEditingProvider] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    displayName: '',
    description: '',
    baseUrl: '',
    models: [] as any[],
    isActive: true
  });

  const [configData, setConfigData] = useState({
    apiKey: '',
    baseUrl: '',
    organizationId: '',
    projectId: '',
    timeout: 30000,
    retryAttempts: 3
  });

  useEffect(() => {
    loadProviders();
  }, [loadProviders]);

  const resetForm = () => {
    setFormData({
      name: '',
      displayName: '',
      description: '',
      baseUrl: '',
      models: [],
      isActive: true
    });
    setConfigData({
      apiKey: '',
      baseUrl: '',
      organizationId: '',
      projectId: '',
      timeout: 30000,
      retryAttempts: 3
    });
  };

  const handleCreateProvider = async () => {
    try {
      await createProvider({
        name: formData.name,
        displayName: formData.displayName,
        description: formData.description,
        baseUrl: formData.baseUrl || undefined,
        models: formData.models
      });

      // Create provider config
      if (configData.apiKey) {
        await saveProviderConfig({
          providerId: formData.name,
          apiKey: configData.apiKey,
          baseUrl: configData.baseUrl || undefined,
          organizationId: configData.organizationId || undefined,
          projectId: configData.projectId || undefined,
          timeout: configData.timeout,
          retryAttempts: configData.retryAttempts
        });
      }

      alert('Provider created successfully');
      setIsCreateDialogOpen(false);
      resetForm();
    } catch (error) {
      alert('Failed to create provider');
      console.error('Error creating provider:', error);
    }
  };

  const handleUpdateProvider = async () => {
    if (!editingProvider) return;

    try {
      await updateProvider(editingProvider, {
        displayName: formData.displayName,
        description: formData.description
      });

      // Update provider config
      if (configData.apiKey) {
        await saveProviderConfig({
          providerId: editingProvider,
          apiKey: configData.apiKey,
          baseUrl: configData.baseUrl || undefined,
          organizationId: configData.organizationId || undefined,
          projectId: configData.projectId || undefined,
          timeout: configData.timeout,
          retryAttempts: configData.retryAttempts
        });
      }

      alert('Provider updated successfully');
      setEditingProvider(null);
      resetForm();
    } catch (error) {
      alert('Failed to update provider');
      console.error('Error updating provider:', error);
    }
  };

  const handleDeleteProvider = async (providerId: string) => {
    if (!confirm('Are you sure you want to delete this provider?')) return;

    try {
      await deleteProvider(providerId);
      alert('Provider deleted successfully');
    } catch (error) {
      alert('Failed to delete provider');
      console.error('Error deleting provider:', error);
    }
  };

  const handleEditProvider = (providerId: string) => {
    const provider = providers.find(p => p.id === providerId);
    const config = providerConfigs[providerId];

    if (provider) {
      setFormData({
        name: provider.name,
        displayName: provider.displayName,
        description: provider.description,
        baseUrl: provider.baseUrl || '',
        models: provider.models,
        isActive: provider.isActive
      });

      setConfigData({
        apiKey: config?.apiKey || '',
        baseUrl: config?.baseUrl || '',
        organizationId: config?.organizationId || '',
        projectId: config?.projectId || '',
        timeout: config?.timeout || 30000,
        retryAttempts: config?.retryAttempts || 3
      });

      setEditingProvider(providerId);
    }
  };

  const handleValidateProvider = async (providerId: string) => {
    try {
      const isValid = await validateProviderConfig(providerId);
      if (isValid) {
        alert('Provider configuration is valid');
      } else {
        alert('Provider configuration is invalid');
      }
    } catch (error) {
      alert('Failed to validate provider configuration');
      console.error('Error validating provider:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading providers...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-red-500">Error loading providers: {error}</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Provider Management</h1>
          <p className="text-muted-foreground">
            Manage your AI providers and their configurations
          </p>
        </div>
        <Button onClick={() => { resetForm(); setIsCreateDialogOpen(true); }}>
          <Plus className="w-4 h-4 mr-2" />
          Add Provider
        </Button>
      </div>

      <div className="grid gap-4">
        {providers.map((provider) => (
          <div key={provider.id} className="border rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <h3 className="text-lg font-semibold">{provider.displayName}</h3>
                <span className={`px-2 py-1 text-xs rounded ${provider.isActive ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                  {provider.isActive ? 'Active' : 'Inactive'}
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleValidateProvider(provider.id)}
                >
                  <CheckCircle className="w-4 h-4" />
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleEditProvider(provider.id)}
                >
                  <Edit className="w-4 h-4" />
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleDeleteProvider(provider.id)}
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </div>

            <p className="text-sm text-gray-600 mb-2">{provider.description}</p>

            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="font-medium">Name:</span>
                <span className="ml-2">{provider.name}</span>
              </div>
              {provider.baseUrl && (
                <div>
                  <span className="font-medium">Base URL:</span>
                  <span className="ml-2">{provider.baseUrl}</span>
                </div>
              )}
              <div>
                <span className="font-medium">Models:</span>
                <span className="ml-2">{provider.models?.length || 0} available</span>
              </div>
              <div>
                <span className="font-medium">API Key:</span>
                <span className="ml-2">
                  {providerConfigs[provider.id]?.apiKey ? '••••••••' : 'Not configured'}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {providers.length === 0 && (
        <div className="text-center py-12">
          <Settings className="w-12 h-12 mx-auto text-gray-400 mb-4" />
          <h3 className="text-lg font-semibold mb-2">No providers configured</h3>
          <p className="text-gray-600 mb-4">
            Add your first AI provider to start using the chat assistant.
          </p>
          <Button onClick={() => setIsCreateDialogOpen(true)}>
            <Plus className="w-4 h-4 mr-2" />
            Add Provider
          </Button>
        </div>
      )}

      {/* Create/Edit Dialog */}
      {(isCreateDialogOpen || editingProvider) && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <h2 className="text-xl font-bold mb-4">
              {editingProvider ? 'Edit Provider' : 'Add New Provider'}
            </h2>

            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Name</label>
                  <Input
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="openai"
                    disabled={!!editingProvider}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Display Name</label>
                  <Input
                    value={formData.displayName}
                    onChange={(e) => setFormData({ ...formData, displayName: e.target.value })}
                    placeholder="OpenAI"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Description</label>
                <Input
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="OpenAI GPT models"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Base URL (Optional)</label>
                <Input
                  value={formData.baseUrl}
                  onChange={(e) => setFormData({ ...formData, baseUrl: e.target.value })}
                  placeholder="https://api.openai.com/v1"
                />
              </div>

              <div className="border-t pt-4">
                <h3 className="text-lg font-semibold mb-4">API Configuration</h3>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">API Key</label>
                    <Input
                      type="password"
                      value={configData.apiKey}
                      onChange={(e) => setConfigData({ ...configData, apiKey: e.target.value })}
                      placeholder="sk-..."
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-1">Organization ID (Optional)</label>
                      <Input
                        value={configData.organizationId}
                        onChange={(e) => setConfigData({ ...configData, organizationId: e.target.value })}
                        placeholder="org-..."
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1">Project ID (Optional)</label>
                      <Input
                        value={configData.projectId}
                        onChange={(e) => setConfigData({ ...configData, projectId: e.target.value })}
                        placeholder="proj_..."
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-1">Timeout (ms)</label>
                      <Input
                        type="number"
                        value={configData.timeout}
                        onChange={(e) => setConfigData({ ...configData, timeout: parseInt(e.target.value) || 30000 })}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1">Retry Attempts</label>
                      <Input
                        type="number"
                        value={configData.retryAttempts}
                        onChange={(e) => setConfigData({ ...configData, retryAttempts: parseInt(e.target.value) || 3 })}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex justify-end space-x-2 mt-6">
              <Button
                variant="outline"
                onClick={() => {
                  setIsCreateDialogOpen(false);
                  setEditingProvider(null);
                  resetForm();
                }}
              >
                Cancel
              </Button>
              <Button onClick={editingProvider ? handleUpdateProvider : handleCreateProvider}>
                {editingProvider ? 'Update' : 'Create'} Provider
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};