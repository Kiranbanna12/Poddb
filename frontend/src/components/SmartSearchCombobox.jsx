import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Search, Plus, Check, X } from 'lucide-react';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Card } from './ui/card';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';

/**
 * SmartSearchCombobox - Reusable component for search with add-new functionality
 * 
 * @param {Object} props
 * @param {string} props.label - Field label
 * @param {string} props.placeholder - Input placeholder
 * @param {Function} props.onSearch - Search function (searchTerm) => Promise<results[]>
 * @param {Function} props.onAddNew - Add new function (data) => Promise<newItem>
 * @param {Function} props.onSelect - Selection callback (selectedItems) => void
 * @param {Array} props.value - Currently selected items
 * @param {boolean} props.multiSelect - Enable multi-selection
 * @param {Object} props.addNewFields - Configuration for add-new form fields
 * @param {string} props.displayKey - Key to display in results (default: 'name')
 * @param {string} props.searchKey - Key to search by (default: 'name')
 */
const SmartSearchCombobox = ({
  label,
  placeholder = "Search...",
  onSearch,
  onAddNew,
  onSelect,
  value = [],
  multiSelect = true,
  addNewFields = [],
  displayKey = 'name',
  searchKey = 'name',
  description
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const [showAddNew, setShowAddNew] = useState(false);
  const [addNewData, setAddNewData] = useState({});
  const [selectedItems, setSelectedItems] = useState(value);
  const dropdownRef = useRef(null);
  const searchTimeout = useRef(null);

  // Update selected items when value prop changes
  useEffect(() => {
    setSelectedItems(value);
  }, [value]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Debounced search
  const handleSearch = useCallback(async (term) => {
    if (searchTimeout.current) {
      clearTimeout(searchTimeout.current);
    }

    searchTimeout.current = setTimeout(async () => {
      setLoading(true);
      try {
        const searchResults = await onSearch(term);
        setResults(searchResults);
        setShowDropdown(true);
      } catch (error) {
        console.error('Search error:', error);
      } finally {
        setLoading(false);
      }
    }, 300);
  }, [onSearch]);

  const handleInputChange = (e) => {
    const term = e.target.value;
    setSearchTerm(term);
    handleSearch(term);
  };

  const handleSelectItem = (item) => {
    let newSelectedItems;
    
    if (multiSelect) {
      // Check if item already selected
      const isSelected = selectedItems.some(selected => selected.id === item.id);
      
      if (isSelected) {
        // Remove item
        newSelectedItems = selectedItems.filter(selected => selected.id !== item.id);
      } else {
        // Add item
        newSelectedItems = [...selectedItems, item];
      }
    } else {
      // Single select
      newSelectedItems = [item];
      setShowDropdown(false);
    }

    setSelectedItems(newSelectedItems);
    onSelect(newSelectedItems);
  };

  const handleRemoveItem = (itemId) => {
    const newSelectedItems = selectedItems.filter(item => item.id !== itemId);
    setSelectedItems(newSelectedItems);
    onSelect(newSelectedItems);
  };

  const isItemSelected = (item) => {
    return selectedItems.some(selected => selected.id === item.id);
  };

  const handleShowAddNew = () => {
    setShowAddNew(true);
    setShowDropdown(false);
    // Pre-fill with search term if applicable
    if (addNewFields.length > 0 && searchTerm) {
      setAddNewData({ [addNewFields[0].name]: searchTerm });
    }
  };

  const handleAddNewFieldChange = (fieldName, value) => {
    setAddNewData(prev => ({ ...prev, [fieldName]: value }));
  };

  const handleSubmitAddNew = async () => {
    try {
      const newItem = await onAddNew(addNewData);
      
      // Add to selected items
      const newSelectedItems = multiSelect ? [...selectedItems, newItem] : [newItem];
      setSelectedItems(newSelectedItems);
      onSelect(newSelectedItems);
      
      // Reset
      setShowAddNew(false);
      setAddNewData({});
      setSearchTerm('');
      
    } catch (error) {
      console.error('Error adding new item:', error);
      alert('Failed to add new item. Please try again.');
    }
  };

  return (
    <div className="space-y-2">
      <Label className="text-[#F5C518]">{label}</Label>
      {description && <p className="text-sm text-gray-400">{description}</p>}
      
      {/* Selected Items as Chips */}
      {selectedItems.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-2">
          {selectedItems.map((item) => (
            <Badge 
              key={item.id} 
              className="bg-[#5799EF] text-white px-3 py-1 flex items-center gap-2"
            >
              {item[displayKey]}
              <X 
                className="w-3 h-3 cursor-pointer hover:text-red-300" 
                onClick={() => handleRemoveItem(item.id)}
              />
            </Badge>
          ))}
        </div>
      )}

      {/* Search Input */}
      <div className="relative" ref={dropdownRef}>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <Input
            type="text"
            placeholder={placeholder}
            value={searchTerm}
            onChange={handleInputChange}
            onFocus={() => {
              if (results.length > 0 || searchTerm) {
                setShowDropdown(true);
              }
            }}
            className="pl-10 bg-[#2A2A2A] border-gray-600 text-white"
          />
        </div>

        {/* Dropdown Results */}
        {showDropdown && (
          <Card className="absolute z-50 w-full mt-1 max-h-60 overflow-y-auto bg-[#1F1F1F] border-gray-700">
            {loading ? (
              <div className="p-4 text-center text-gray-400">Searching...</div>
            ) : results.length === 0 ? (
              <div className="p-4 text-center text-gray-400">
                No results found
              </div>
            ) : (
              <div>
                {results.map((item) => (
                  <div
                    key={item.id}
                    onClick={() => handleSelectItem(item)}
                    className={`p-3 cursor-pointer hover:bg-[#2A2A2A] border-b border-gray-800 flex items-center justify-between ${
                      isItemSelected(item) ? 'bg-[#2A2A2A]' : ''
                    }`}
                  >
                    <div>
                      <div className="text-white">{item[displayKey]}</div>
                      {item.podcast_count !== undefined && (
                        <div className="text-xs text-gray-400">{item.podcast_count} podcasts</div>
                      )}
                      {item.native_name && (
                        <div className="text-xs text-gray-400">{item.native_name}</div>
                      )}
                    </div>
                    {isItemSelected(item) && (
                      <Check className="w-5 h-5 text-[#5799EF]" />
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* Add New Option */}
            {onAddNew && (
              <div
                onClick={handleShowAddNew}
                className="p-3 cursor-pointer hover:bg-[#2A2A2A] border-t border-gray-700 flex items-center gap-2 text-[#5799EF]"
              >
                <Plus className="w-4 h-4" />
                <span>Add "{searchTerm || 'new item'}"</span>
              </div>
            )}
          </Card>
        )}
      </div>

      {/* Add New Form */}
      {showAddNew && (
        <Card className="p-4 bg-[#1F1F1F] border-gray-700 space-y-3">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-lg font-semibold text-[#F5C518]">Add New {label}</h3>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                setShowAddNew(false);
                setAddNewData({});
              }}
              className="text-gray-400"
            >
              <X className="w-4 h-4" />
            </Button>
          </div>

          {addNewFields.map((field) => (
            <div key={field.name} className="space-y-1">
              <Label className="text-gray-300">{field.label}</Label>
              {field.type === 'textarea' ? (
                <Textarea
                  value={addNewData[field.name] || ''}
                  onChange={(e) => handleAddNewFieldChange(field.name, e.target.value)}
                  placeholder={field.placeholder}
                  className="bg-[#2A2A2A] border-gray-600 text-white"
                  rows={field.rows || 3}
                />
              ) : (
                <Input
                  type={field.type || 'text'}
                  value={addNewData[field.name] || ''}
                  onChange={(e) => handleAddNewFieldChange(field.name, e.target.value)}
                  placeholder={field.placeholder}
                  className="bg-[#2A2A2A] border-gray-600 text-white"
                />
              )}
              {field.description && (
                <p className="text-xs text-gray-400">{field.description}</p>
              )}
            </div>
          ))}

          <div className="flex gap-2 pt-2">
            <Button
              onClick={handleSubmitAddNew}
              className="bg-[#5CB85C] hover:bg-[#4CAF50] text-white flex-1"
            >
              Add {label}
            </Button>
            <Button
              variant="outline"
              onClick={() => {
                setShowAddNew(false);
                setAddNewData({});
              }}
              className="border-gray-600 text-gray-300"
            >
              Cancel
            </Button>
          </div>
        </Card>
      )}
    </div>
  );
};

export default SmartSearchCombobox;
