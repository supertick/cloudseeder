import { useState } from "react"

export default function Home({ initialWidgets }) {
  const [widgets, setWidgets] = useState(initialWidgets)
  const [showForm, setShowForm] = useState(false)
  const [newWidgetName, setNewWidgetName] = useState("")

  // Add a new widget
  const handleAddWidget = async () => {
    if (newWidgetName.trim() !== "") {
      const newWidget = { name: newWidgetName.trim() }

      // Post to backend
      const response = await fetch("/api/widgets", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newWidget)
      })
      const createdWidget = await response.json()

      setWidgets([...widgets, createdWidget])
      setNewWidgetName("")
      setShowForm(false)
    }
  }

  // Delete a widget
  const handleDeleteWidget = async (id) => {
    // Call backend to delete the widget
    await fetch(`/api/widgets/${id}`, { method: "DELETE" })

    // Remove from the state
    setWidgets(widgets.filter(widget => widget.id !== id))
  }

  return (
    <div style={{ padding: "20px" }}>
      <h1>Widgets</h1>

      {/* Table of widgets */}
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <th style={{ border: "1px solid #ccc", padding: "8px" }}>Name</th>
            <th style={{ border: "1px solid #ccc", padding: "8px" }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {widgets.map(widget => (
            <tr key={widget.id}>
              <td style={{ border: "1px solid #ccc", padding: "8px" }}>{widget.name}</td>
              <td style={{ border: "1px solid #ccc", padding: "8px", textAlign: "center" }}>
                {/* Delete button */}
                <button
                  onClick={() => handleDeleteWidget(widget.id)}
                  style={{
                    backgroundColor: "red",
                    color: "white",
                    border: "none",
                    padding: "5px 10px",
                    cursor: "pointer"
                  }}
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Add Widget Button */}
      <button
        onClick={() => setShowForm(!showForm)}
        style={{
          marginTop: "20px",
          backgroundColor: "green",
          color: "white",
          border: "none",
          padding: "10px 20px",
          cursor: "pointer"
        }}
      >
        {showForm ? "Cancel" : "Add Widget"}
      </button>

      {/* Add Widget Form */}
      {showForm && (
        <div style={{ marginTop: "20px" }}>
          <input
            type="text"
            value={newWidgetName}
            onChange={(e) => setNewWidgetName(e.target.value)}
            placeholder="Enter widget name"
            style={{ padding: "10px", marginRight: "10px", width: "60%" }}
          />
          <button
            onClick={handleAddWidget}
            style={{
              backgroundColor: "blue",
              color: "white",
              border: "none",
              padding: "10px 20px",
              cursor: "pointer"
            }}
          >
            Add Widget
          </button>
        </div>
      )}
    </div>
  )
}

// Fetch widgets from the backend
export async function getStaticProps() {
  const response = await fetch("http://localhost:3000/widgets")
  const initialWidgets = await response.json()

  return {
    props: { initialWidgets }
  }
}
