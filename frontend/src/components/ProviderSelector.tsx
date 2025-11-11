import React from 'react';
import { useProvidersStore } from '../stores/providersStore';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { ChevronDown, Settings, Check, AlertTriangle } from 'lucide-react';

interface ProviderSelectorProps {
  selectedProviderId?: string;
  onProviderChange: (providerId: string) => void;
  className?: string;
}

export const ProviderSelector: React.FC<ProviderSelectorProps> = ({
  selectedProviderId,
  onProviderChange,
  className = ''
}) => {
  const { providers, getActiveProviders, getProviderConfig } = useProvidersStore();
  const [isOpen, setIsOpen] = React.useState(false);

  const activeProviders = getActiveProviders();
  const selectedProvider = providers.find(p => p.id === selectedProviderId) || activeProviders[0];

  const handleProviderSelect = (providerId: string) => {
    onProviderChange(providerId);
    setIsOpen(false);
  };

  return (
    <div className={`relative ${className}`}>
      <Button
        variant="outline"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 min-w-[200px] justify-between"
      >
        <div className="flex items-center gap-2">
          <Settings className="w-4 h-4" />
          <span className="truncate">
            {selectedProvider?.displayName || 'Select Provider'}
          </span>
        </div>
        <ChevronDown className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </Button>

      {isOpen && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-slate-800 border border-slate-700 rounded-md shadow-lg z-50 max-h-60 overflow-y-auto">
          {activeProviders.length === 0 ? (
            <div className="p-4 text-center text-slate-400">
              <Settings className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">No active providers</p>
              <p className="text-xs">Configure providers in Settings</p>
            </div>
          ) : (
            activeProviders.map((provider) => {
              const config = getProviderConfig(provider.id);
              const isConfigured = !!(config?.apiKey && config.apiKey.length > 0);
              
              return (
                <button
                  key={provider.id}
                  onClick={() => isConfigured && handleProviderSelect(provider.id)}
                  disabled={!isConfigured}
                  className={`w-full text-left px-4 py-3 hover:bg-slate-700 transition-colors ${
                    selectedProvider?.id === provider.id ? 'bg-slate-700 text-blue-400' : 'text-slate-200'
                  } ${!isConfigured ? 'opacity-60 cursor-not-allowed' : ''}`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      {selectedProvider?.id === provider.id && (
                        <Check className="w-4 h-4 text-blue-400" />
                      )}
                      {!isConfigured && (
                        <AlertTriangle className="w-4 h-4 text-yellow-500" />
                      )}
                      <div>
                        <div className="font-medium">{provider.displayName}</div>
                        <div className="text-xs text-slate-400">{provider.description}</div>
                        {!isConfigured && (
                          <div className="text-xs text-yellow-500">API key not configured</div>
                        )}
                      </div>
                    </div>
                    <div className="text-xs text-slate-500">
                      {provider.models?.length || 0} models
                    </div>
                  </div>
                </button>
              );
            })
          )}
        </div>
      )}

      {/* Overlay to close dropdown when clicking outside */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
};